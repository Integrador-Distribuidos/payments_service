from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Invoice
from rest_framework.permissions import AllowAny

class SalesReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        invoices = Invoice.objects.filter(status="completed")

        try:
            if start_date:
                start_date_obj = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
                invoices = invoices.filter(time__gte=start_date_obj)
            if end_date:
                end_date_obj = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))
                invoices = invoices.filter(time__lt=end_date_obj) 
        except ValueError:
            return Response(
                {"error": "Formato da data inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_vendas = invoices.count()
        valor_total = invoices.aggregate(total=Sum("value"))["total"] or 0

        return Response({
            "total_vendas": total_vendas,
            "valor_total": float(valor_total),
            "periodo": {
                "inicio": start_date,
                "fim": end_date
            }
        }, status=status.HTTP_200_OK)
