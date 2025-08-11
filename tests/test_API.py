import pytest
from rest_framework.test import APIClient
from rest_framework import status
from json import load
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import os
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def create_test_token(user_id: str = "1000"):
    payload = {
        "user_id": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=300)  # expira em 300 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

AUTH_TOKEN = create_test_token()
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

@pytest.mark.django_db
def test_create_and_update_payment():
    client = APIClient()
    client.credentials(**HEADERS)

    # Payload para criar o pagamento
    payload_create = {
        "payment_type": "PIX",
        "status": "pending",
        "value": "-675080632516196.6",
        "user_id": 2147483647,
        "id_order": 2147483647,
        "user_cpf": "string"
    }
    
    # Endpoint de criação
    url_create = "/api/invoices/"
    response_create = client.post(url_create, payload_create, format="json")
    
    print("POST status:", response_create.status_code, response_create.json())
    assert response_create.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    
    data_create = response_create.json()
    payment_id = data_create.get("id")  # Ajuste o campo 'id' conforme sua API
    
    assert payment_id is not None, "Resposta da criação não retornou o ID"
    
    # Agora o payload para atualizar (PUT)
    payload_update = {
        "payment_type": "PIX",
        "status": "completed",  # Exemplo: alterar o status
        "value": "-675080632516196.6",
        "user_id": 2147483647,
        "id_order": 2147483647,
        "user_cpf": "string"
    }
    
    # Endpoint para atualizar, incluindo o ID
    url_update = f"/api/invoices/{payment_id}/"
    response_update = client.put(url_update, payload_update, format="json")
    
    print("PUT status:", response_update.status_code, response_update.json())
    assert response_update.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
    
    data_update = response_update.json()
    assert data_update.get("status") == "completed"

@pytest.mark.django_db
def test_patch_and_delete_payment():
    client = APIClient()
    client.credentials(**HEADERS)

    # Criar o recurso
    payload_create = {
        "payment_type": "PIX",
        "status": "pending",
        "value": "-331309744383008",
        "user_id": 2147483647,
        "id_order": 2147483647,
        "user_cpf": "string"
    }
    url_create = "/api/invoices/"
    response_create = client.post(url_create, payload_create, format="json")
    assert response_create.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    data_create = response_create.json()
    payment_id = data_create.get("id")
    assert payment_id is not None

    # Atualizar parcialmente com PATCH
    patch_payload = {
        "status": "completed"
    }
    url_patch = f"/api/invoices/{payment_id}/"
    response_patch = client.patch(url_patch, patch_payload, format="json")
    assert response_patch.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]

    data_patch = response_patch.json()
    assert data_patch.get("status") == "completed"

    # Deletar o recurso com DELETE
    url_delete = f"/api/invoices/{payment_id}/"
    response_delete = client.delete(url_delete)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

    # Opcional: tentar buscar para confirmar que foi deletado (deve dar 404)
    response_get = client.get(url_delete)
    assert response_get.status_code == status.HTTP_404_NOT_FOUND
