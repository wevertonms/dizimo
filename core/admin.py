from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest

from core.models import Perfil


def get_permission(model, permission: str):
    model_content_type = ContentType.objects.get_for_model(model)
    model_permissions = Permission.objects.filter(content_type=model_content_type)
    return model_permissions.get(codename__startswith=permission)


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    view_on_site = False
    verbose_name_plural = "Perfil"
    extra = 1

    def get_readonly_fields(self, request: HttpRequest, obj: Perfil):  # noqa
        fields = ["user"]
        user = request.user
        is_superuser = user.is_superuser
        if not is_superuser:
            if hasattr(obj, "user"):
                if obj.user != user:
                    fields += [
                        "nome",
                        "endereco",
                        "nascimento",
                        "genero",
                        "telefone",
                        "email",
                    ]
            return fields
        return tuple()


# Unregister the provided model admin
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ["date_joined"]
    list_filter = []
    inlines = [PerfilInline]

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        return qs.filter(username=user.username)

    def get_form(self, request: HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set(["last_login"])
        if not is_superuser:
            if request.user == obj:
                disabled_fields |= {
                    "username",
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                }
            else:
                disabled_fields = set(form.base_fields)
        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        return form

    def save_model(self, request: HttpRequest, obj: User, form, change):
        obj.registrado_por = request.user
        is_new_user = not obj.pk
        if is_new_user:
            obj.is_staff = True
        super().save_model(request, obj, form, change)
        if is_new_user:
            new_user_permissions = [
                get_permission(User, "view"),
                get_permission(User, "change"),
            ]
            obj.user_permissions.set(new_user_permissions)
