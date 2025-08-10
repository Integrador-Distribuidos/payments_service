from functools import partialmethod

import requests
from requests import HTTPError
from django.contrib.auth import get_user_model
from .api.serializers import AsaasCustomerSerializer
import os
from dotenv import load_dotenv
import json
import re
User = get_user_model()

load_dotenv()



ASAAS_ENDPOINT_URL = "https://sandbox.asaas.com/api/v3"
ASAAS_ACCESS_TOKEN = os.getenv('ASAAS_API_KEY')

class AssasPaymentClient:
    error_msgs = {
        400: "Envio de dados inválidos",
        401: "Chave de API inválida",
        500: "Erro no servidor",
    }

    def __init__(self, **kwargs):
        self.endpoint_url = ASAAS_ENDPOINT_URL
        self.request_headers = {
            "access_token": ASAAS_ACCESS_TOKEN,
            "accept": "application/json",
            "content-type": "application/json",
        }

    def _request(self, method, url, **kwargs):
        response = requests.request(
            method,
            self.endpoint_url + url,
            headers=self.request_headers,
            **kwargs,
        )
        try:
            response.raise_for_status()
        except HTTPError:
            raise HTTPError(
                self.error_msgs.get(response.status_code, "Erro desconhecido"),
                response=response,
            )
        return response.json()

    _api_get = partialmethod(_request, "get")
    _api_put = partialmethod(_request, "put")
    _api_post = partialmethod(_request, "post")

    def create_or_update_customer(self, invoice, **kwargs):
        user_cpf = re.sub(r'\D', '', str(invoice.user_cpf))

        try:
            user = User.objects.get(id=invoice.user_id)
            name = user.get_full_name() or str(user)
            email = getattr(user, "email", None)
        except User.DoesNotExist:
            name = f"Cliente {invoice.user_id}"
            email = None

        customer_payload = {
            "name": name,
            "cpfCnpj": user_cpf,
            "email": email,
            "externalReference": str(invoice.user_id),
        }

        customer_payload = {k: v for k, v in customer_payload.items() if v is not None}

        customer_id = self._get_customer_id(user_cpf)
        if customer_id:
            return self._update_customer(customer_id, customer_payload)
        else:
            return self._create_customer(customer_payload)


    def _get_customer_id(self, user_cpf):
        response = self._api_get(f"/customers?cpfCnpj={user_cpf}")
        if response.get("totalCount", 0) > 0:
            return response["data"][0]["id"]
        return None

    def _update_customer(self, customer_id, data):
        return self._api_put(f"/customers/{customer_id}", json=data)

    def _create_customer(self, data):
        print(">>> Enviando para Asaas:", json.dumps(data, ensure_ascii=False, indent=2))
        return self._api_post("/customers", json=data)

    def send_payment_request(self, data):
        return self._api_post("/payments", json=data)

    def get_qr_code(self, id):
        return self._api_get(f"/payments/{id}/pixQrCode")

    def send_withdraw_request(self, data):
        return self._api_post("/transfers", json=data)