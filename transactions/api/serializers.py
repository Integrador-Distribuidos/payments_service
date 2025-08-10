from rest_framework import serializers
from transactions.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "external_id",
            "payment_type",
            "status",
            "link_payment",
            "value",
            "time",
            "user_id",
            "id_order",
            "user_cpf",
        ]

    external_id = serializers.CharField(read_only=True)
    link_payment = serializers.CharField(read_only=True)

class CreateInvoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, value):
        try:
            invoice = Invoice.objects.get(id=value)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Fatura não encontrada.")
        return value


class WithDrawSerializer(serializers.Serializer):
    value = serializers.FloatField()


class CPFField(serializers.Field):
    def to_representation(self, value):
        return str(value)

class AsaasCustomerSerializer(serializers.Serializer):
    externalReference = serializers.CharField(source="id")
    """name = serializers.SerializerMethodField()
    cpfCnpj = CPFField(source="cpf")
    email = serializers.EmailField()"""

    """def get_name(self, obj):
        return obj.get_full_name()
"""