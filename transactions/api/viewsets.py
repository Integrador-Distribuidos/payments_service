from datetime import datetime, timedelta
import json
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q

from transactions.models import Invoice
from .serializers import CreateInvoiceSerializer, WithDrawSerializer, InvoiceSerializer
from ..asaas import AssasPaymentClient


class InvoiceViewSet(ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    @action(detail=False, methods=['get'])
    def get_invoice_by_order_id(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({"error": "Parâmetro 'id' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.filter(id_order=id).first()
        if invoice:
            serializer = self.get_serializer(invoice)
            return Response(serializer.data)
        return Response({"error": "Pedido não encontrado"}, status=status.HTTP_404_NOT_FOUND)


class InvoicesAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    @extend_schema(request=CreateInvoiceSerializer)
    def post(self, request):
        serializer = CreateInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice_id = serializer.validated_data["id"]
            invoice = Invoice.objects.get(id=invoice_id)  # Utilize o id do invoice aqui

            client = AssasPaymentClient()

            # Você deve buscar o CPF do usuário via API externa
            # Aqui estamos considerando que o invoice já tem o CPF
            customer = client.create_or_update_customer(invoice.user_id)
            data = self.prepare_payment_data(invoice, customer)
            response = self.send_payment_request(data)

            if response:
                self.update_invoice(invoice, response)
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Erro ao enviar solicitação de pagamento"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def prepare_payment_data(self, invoice, customer):
        end_date = datetime.now() + timedelta(days=1)
        end_date_str = end_date.strftime("%Y-%m-%d")
        data = {
            "customer": customer.get("id"),
            "billingType": invoice.payment_type,
            "value": float(invoice.value),
            "dueDate": end_date_str,
            "description": f"Pagamento do pedido #{invoice.id_order}",
            "externalReference": str(invoice.id),  # Passando o id corretamente
            "cpfCnpj": str(invoice.user_id.cpf),
        }
        return data

    def send_payment_request(self, data):
        client = AssasPaymentClient()
        response = client.send_payment_request(data)
        return response

    def update_invoice(self, invoice, result):
        invoice.link_payment = result.get("invoiceUrl", "")
        invoice.external_id = result.get("id", "")
        invoice.save()


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=WithDrawSerializer)
    def post(self, request):
        serializer = WithDrawSerializer(data=request.data)
        if serializer.is_valid():
            value = serializer.validated_data["value"]
            user_cpf = request.user.cpf  # CPF deve estar disponível no token do usuário autenticado

            # Você pode buscar saldo via API, caso não esteja no token
            if request.user.balance < value:
                return Response(
                    {"error": "Saldo insuficiente para saque"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = self.prepare_payment_data(user_cpf, value)
            response = self.send_payment_request(data)

            if response:
                # Você pode disparar uma requisição para o microsserviço de usuários para atualizar saldo
                return Response(response, status=status.HTTP_200_OK)

        return Response(
            {"error": "Erro ao enviar solicitação de pagamento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def prepare_payment_data(self, cpf, value):
        return {
            "value": value,
            "pixAddressKey": str(cpf),
            "pixAddressKeyType": "CPF",
            "scheduleDate": None,
            "description": "Saque da plataforma Stock2Sell",
        }

    def send_payment_request(self, data):
        client = AssasPaymentClient()
        return client.send_withdraw_request(data)


class QRCodeView(APIView):
    @extend_schema(request=CreateInvoiceSerializer)
    def post(self, request):
        serializer = CreateInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice_id = serializer.validated_data["id"]
            invoice = Invoice.objects.get(id=invoice_id)  # Certificando que o id é usado aqui

            client = AssasPaymentClient()
            response = client.get_qr_code(invoice.external_id)

            if response:
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Erro ao gerar QR Code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebHookview(APIView):
    def post(self, request):
        data = json.loads(request.body)
        print(data)
        if data:
            # Aqui você pode processar o callback do Asaas, ex: alterar status da fatura
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
