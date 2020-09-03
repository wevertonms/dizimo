import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings


class Igreja(models.Model):
    nome = models.CharField(_("Nome"), max_length=50)
    endereco = models.CharField(_("Endereço"), max_length=255, null=True)

    class Meta:
        verbose_name = _("Igreja")
        verbose_name_plural = _("Igrejas")

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("Igreja_detail", kwargs={"pk": self.pk})


class Dizimista(models.Model):
    nome = models.CharField(_("Nome completo"), max_length=50, null=False)
    blank = dict(blank=True, null=True)
    endereco = models.CharField(_("Endereço"), max_length=255, **blank)
    nascimento = models.DateField(_("Data de nascimento"), **blank)
    generos = [("F", _("Feminino")), ("M", _("Masculino")), ("O", _("Outro"))]
    genero = models.CharField(max_length=1, choices=generos, default=generos[0][0])
    telefone = models.CharField(_("Telefone"), max_length=17, **blank)
    email = models.EmailField(_("Email"), **blank)
    igreja = models.ForeignKey("gestao.Igreja", on_delete=models.DO_NOTHING, null=True)

    class Meta:
        verbose_name = _("Dizimista")
        verbose_name_plural = _("Dizimistas")

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("Dizimista_detail", kwargs={"pk": self.pk})


class Pagamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    igreja = models.ForeignKey("gestao.Igreja", on_delete=models.DO_NOTHING)
    dizimista = models.ForeignKey("gestao.Dizimista", on_delete=models.DO_NOTHING)
    data = models.DateTimeField(_("Data e hora"), default=timezone.now)
    valor = models.DecimalField(_("Valor"), max_digits=14, decimal_places=2)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Registrado por"),
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = _("Pagamento")
        verbose_name_plural = _("Pagamentos")

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse("Pagamento_detail", kwargs={"pk": self.pk})
