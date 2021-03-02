from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

FEMININO = ("F", _("Feminino"))
MASCULINO = ("M", _("Masculino"))
OUTRO = ("O", _("Outro"))

GENEROS = (FEMININO, MASCULINO, OUTRO)


class Perfil(models.Model):
    blank_opts = dict(blank=True, null=True)
    user = models.OneToOneField(
        User, verbose_name=_("Usuário"), on_delete=models.CASCADE, **blank_opts
    )
    nome = models.CharField(_("Nome completo"), max_length=50)
    endereco = models.CharField(_("Endereço"), max_length=255, **blank_opts)
    nascimento = models.DateField(_("Data de nascimento"), **blank_opts)
    genero = models.CharField(
        _("Gênero"), max_length=1, choices=GENEROS, default=FEMININO[0]
    )
    telefone = models.CharField(_("Telefone"), max_length=20, **blank_opts)
    email = models.EmailField(_("Email"), **blank_opts)

    class Meta:
        verbose_name = _("Perfil")
        verbose_name_plural = _("Perfil")

    def __str__(self):
        if self.user:
            return f"{self.nome} ({self.user.username})"
        return f"{self.nome}"

    def get_absolute_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=[self.pk],
        )
