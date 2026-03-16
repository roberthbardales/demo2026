from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import View, ListView
from django.views.generic.edit import FormView

from .forms import UserRegisterForm, LoginForm, UpdatePasswordForm
from .models import User
from .mixins import SuperusuarioMixin, UsuarioListaMixin


class UserRegisterView(SuperusuarioMixin, FormView):
    """Solo superusuario puede registrar nuevos usuarios."""
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users_app:user-lista')

    def form_valid(self, form):
        User.objects.create_user(
            form.cleaned_data['email'],
            form.cleaned_data['password1'],
            full_name=form.cleaned_data['full_name'],
            occupation=form.cleaned_data['occupation'],
            genero=form.cleaned_data['genero'],
            date_birth=form.cleaned_data['date_birth'],
            avatar=form.cleaned_data.get('avatar'),
        )
        return super().form_valid(form)


class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home_app:dashboard')  # fallback por defecto

    def form_valid(self, form):
        user = authenticate(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)

        # Redirigir según rol
        if user.is_superuser or user.occupation == User.ADMIN:
            return HttpResponseRedirect(reverse('users_app:user-lista'))
        elif user.occupation == User.RRHH:
            return HttpResponseRedirect(reverse('rrhh_app:dashboard'))
        elif user.occupation == User.INVENTARIO:
            return HttpResponseRedirect(reverse('inventario_app:dashboard'))
        elif user.occupation == User.EMPLEADO:
            return HttpResponseRedirect(reverse('home_app:dashboard'))
        else:
            return HttpResponseRedirect(reverse('home_app:dashboard'))


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('users_app:user-login'))


class UpdatePasswordView(LoginRequiredMixin, FormView):
    """Cualquier usuario logueado puede cambiar su contraseña."""
    template_name = 'users/cambiar_contraseña.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('users_app:user-login')
    login_url = reverse_lazy('users_app:user-login')

    def form_valid(self, form):
        usuario = self.request.user
        user = authenticate(
            email=usuario.email,
            password=form.cleaned_data['password1']
        )
        if user:
            usuario.set_password(form.cleaned_data['password2'])
            usuario.save()
        logout(self.request)
        return super().form_valid(form)


class UserListView(UsuarioListaMixin, ListView):
    """Admin y RRHH pueden ver la lista de usuarios."""
    template_name = 'users/lista_usuarios.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.usuarios_sistema()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['total_admin']      = qs.filter(occupation=User.ADMIN).count()
        ctx['total_rrhh']       = qs.filter(occupation=User.RRHH).count()
        ctx['total_inventario'] = qs.filter(occupation=User.INVENTARIO).count()
        ctx['total_empleado']   = qs.filter(occupation=User.EMPLEADO).count()
        return ctx