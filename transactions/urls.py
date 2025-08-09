from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesReportView

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
    path('', include(router.urls)),

    path('transactions/process_payment', InvoicesAPIView.as_view(), name='create-invoice'),
    path('transactions/withdraw', WithdrawView.as_view(), name='withdraw'),
    path('transactions/get_qr_code', QRCodeView.as_view(), name='qr-code'),
    path('transactions/payment_webhook', PaymentWebHookview.as_view(), name='webhook'),
    path('invoices/sales_report/', SalesReportView.as_view(), name='sales-report'),
]