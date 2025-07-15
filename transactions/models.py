from django.db import models
from django.utils.translation import gettext as _

STATUS_GROUP_CHOICES = (
    ("pending", _("Aguardando pagamento")),
    ("completed", _("Pagamento concluído")),
    ("canceled", _("Pagamento Cancelado")),
)


class Invoice(models.Model):
    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"

    PAYMENT_METHODS_CHOICES = (
        ("PIX", _("Pix")),
        ("CREDIT_CARD", _("Cartão de crédito")),
    )

    PAYMENT_STATUS_CHOICES = (
        ("PENDING", _("Pendente")),
        ("RECEIVED", _("Recebido")),
        ("CONFIRMED", _("Confirmado")),
        ("CANCELED", _("Cancelado")),
    )

    external_id = models.CharField(
        max_length=50,
        editable=False,
        verbose_name=_("ID externo"),
        null=True,
        blank=True,
    )
    payment_type = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS_CHOICES,
        verbose_name=_("Tipo do pagamento"),
    )
    link_payment = models.CharField(
        max_length=500,
        verbose_name=_("Link do pagamento"),
        null=True,
        blank=True,
    )
    value = models.DecimalField(verbose_name="Valor", max_digits=20, decimal_places=2)
    time = models.DateTimeField(verbose_name="Data/Hora", auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_GROUP_CHOICES,
        null=False,
        default="pending",
        verbose_name=_("Status"),
    )

    user_id = models.IntegerField(verbose_name="ID do Usuário")

    id_order = models.IntegerField(
        verbose_name="ID do Pedido", null=True, blank=True
    )
