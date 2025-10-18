import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from core.models import Perfil


class Igreja(models.Model):
    nome = models.CharField("Nome", max_length=50)
    endereco = models.CharField("Endereço", max_length=255, null=True)
    gestores = models.ManyToManyField(User, related_name="gestor_em")
    agentes = models.ManyToManyField(User, related_name="agente_em")

    dizimista_set: models.QuerySet["Dizimista"]

    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=(self.pk,),
        )

    def número_de_dizimistas(self):
        return self.dizimista_set.count()


class PerfilDizimista(Perfil):
    dizimista = models.OneToOneField(
        "gestao.Dizimista",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="perfil",
    )


class Dizimista(models.Model):
    igreja = models.ForeignKey("gestao.Igreja", on_delete=models.SET_NULL, null=True)
    dizimo = models.DecimalField("Dízimo", max_digits=14, decimal_places=2, null=True)

    class Meta:
        verbose_name = "Dizimista"
        verbose_name_plural = "Dizimistas"

    def __str__(self):
        return f"{self.perfil}"

    @property
    def perfil(self):
        return self.perfil

    @property
    def nascimento(self):
        return self.perfil.nascimento

    def get_absolute_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=(self.pk,),
        )

    def link(self):
        url = self.get_absolute_url()
        display_text = f"<a href={url}>{self}</a>"
        return format_html(display_text)

    link.short_description = Meta.verbose_name


class Pagamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dizimista = models.ForeignKey(Dizimista, on_delete=models.SET_NULL, null=True)
    data = models.DateTimeField("Data e hora", default=timezone.now)
    valor = models.DecimalField("Valor", max_digits=14, decimal_places=2)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Registrado por",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-data"]

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_view",
            args=(self.pk,),
        )

    @property
    def mês(self):
        return self.data.strftime("%m/%Y")


class ResumoPagamentos(Pagamento):
    class Meta:
        proxy = True
        verbose_name = "Resumo de pagamentos"
        verbose_name_plural = "Resumos de pagamentos"
