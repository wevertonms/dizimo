import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.html import format_html


class Igreja(models.Model):
    nome = models.CharField(_("Nome"), max_length=50)
    endereco = models.CharField(_("Endereço"), max_length=255, null=True)
    gestores = models.ManyToManyField(User, related_name="gestor_em")
    agentes = models.ManyToManyField(User, related_name="agente_em")

    class Meta:
        verbose_name = _("Igreja")
        verbose_name_plural = _("Igrejas")

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=(self.pk,),
        )

    def número_de_dizimistas(self):
        return self.dizimista_set.count()


class Dizimista(models.Model):
    nome = models.CharField(_("Nome completo"), max_length=50, null=False)
    blank = dict(blank=True, null=True)
    endereco = models.CharField(_("Endereço"), max_length=255, **blank)
    nascimento = models.DateField(_("Data de nascimento"), **blank)
    generos = [("F", _("Feminino")), ("M", _("Masculino")), ("O", _("Outro"))]
    genero = models.CharField(max_length=1, choices=generos, default=generos[0][0])
    telefone = models.CharField(_("Telefone"), max_length=20, **blank)
    email = models.EmailField(_("Email"), **blank)
    igreja = models.ForeignKey("gestao.Igreja", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("Dizimista")
        verbose_name_plural = _("Dizimistas")

    def __str__(self):
        return self.nome

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
    igreja = models.ForeignKey("gestao.Igreja", on_delete=models.DO_NOTHING)
    dizimista = models.ForeignKey(
        "gestao.Dizimista", on_delete=models.SET_NULL, null=True
    )
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
        ordering = ["-data"]

    def __str__(self):
        return str(self.id)  # f"R$ {self.valor} em {self.data}"

    def get_absolute_url(self):
        reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_view",
            args=(self.pk,),
        )


class RelatorioPagamentos(Pagamento):
    class Meta:
        proxy = True
        verbose_name = "Relatório de Pagamentos"
        verbose_name_plural = "Relatórios de Pagamentos"
