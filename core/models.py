from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

FEMININO = ("F", "Feminino")
MASCULINO = ("M", "Masculino")
OUTRO = ("O", "Outro")

GENEROS = (FEMININO, MASCULINO, OUTRO)


blank_opts = dict(blank=True, null=True)


class Perfil(models.Model):
    user = models.OneToOneField(
        User, verbose_name="Usuário", on_delete=models.CASCADE, **blank_opts
    )
    nome = models.CharField("Nome completo", max_length=50)
    endereco = models.CharField("Endereço", max_length=255, **blank_opts)
    nascimento = models.DateField("Data de nascimento", **blank_opts)
    genero = models.CharField(
        "Gênero", max_length=1, choices=GENEROS, default=FEMININO[0]
    )
    telefone = models.CharField("Telefone", max_length=20, **blank_opts)
    email = models.EmailField("Email", **blank_opts)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfil"

    def __str__(self):
        if self.user:
            return f"{self.nome} ({self.user.username})"
        return f"{self.nome}"

    def get_absolute_url(self):
        return reverse(
            f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
            args=[self.pk],
        )
