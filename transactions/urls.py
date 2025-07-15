from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.viewsets import (
    InvoiceViewSet,
    InvoicesAPIView,
    WithdrawView,
    QRCodeView,
    PaymentWebHookview,
)

router = DefaultRouter()
router.register('invoices', InvoiceViewSet, basename='invoices')

urlpatterns = [
    # ViewSet com rota REST padrão
    path('', include(router.urls)),

    # Endpoints específicos
    path('invoices/create/', InvoicesAPIView.as_view(), name='create-invoice'),
    path('invoices/withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('invoices/qr-code/', QRCodeView.as_view(), name='qr-code'),
    path('invoices/webhook/', PaymentWebHookview.as_view(), name='webhook'),
]