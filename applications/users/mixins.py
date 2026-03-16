from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import User


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────

def es_admin_o_super(user):
    return user.is_superuser or user.occupation == User.ADMIN


# ─────────────────────────────────────────
# Base permisos
# ─────────────────────────────────────────

class BasePermisoMixin(LoginRequiredMixin):

    login_url = reverse_lazy('users_app:user-login')
    occupations_permitidas = []
    solo_lectura = False

    def dispatch(self, request, *args, **kwargs):

        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        # superusuario acceso total
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # admin acceso total
        if user.occupation == User.ADMIN:
            return super().dispatch(request, *args, **kwargs)

        # validar acceso por rol
        if user.occupation not in self.occupations_permitidas:
            raise PermissionDenied

        # empleado solo lectura
        if (
            self.solo_lectura
            and user.occupation == User.EMPLEADO
            and request.method in ["POST", "PUT", "DELETE"]
        ):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────
# Solo superusuario
# ─────────────────────────────────────────

class SuperusuarioMixin(LoginRequiredMixin):

    login_url = reverse_lazy('users_app:user-login')

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_superuser:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────
# Mixins por módulo
# ─────────────────────────────────────────

# Dashboard
class DashboardMixin(BasePermisoMixin):

    occupations_permitidas = [
        User.ADMIN,
        User.RRHH,
        User.INVENTARIO,
        User.EMPLEADO,
    ]


# RRHH
class RRHHMixin(BasePermisoMixin):

    occupations_permitidas = [
        User.ADMIN,
        User.RRHH,
        User.EMPLEADO,
    ]

    solo_lectura = True


# Inventario
class InventarioMixin(BasePermisoMixin):

    occupations_permitidas = [
        User.ADMIN,
        User.INVENTARIO,
        User.EMPLEADO,
    ]

    solo_lectura = True


# Usuarios
class UsuarioListaMixin(BasePermisoMixin):

    occupations_permitidas = [
        User.ADMIN,
        User.RRHH,
    ]

    solo_lectura = True


# ─────────────────────────────────────────
# Compatibilidad con código antiguo
# ─────────────────────────────────────────

class AdministradorPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.ADMIN]


class RRHHPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.RRHH]


class InventarioPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.INVENTARIO]


class EmpleadoPermisoMixin(BasePermisoMixin):
    occupations_permitidas = [User.EMPLEADO]