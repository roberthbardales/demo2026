from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):  # models.Manager es redundante

    def _create_user(self, email, password, is_staff, is_superuser, is_active, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')  # validación mínima
        email = self.normalize_email(email)  # normaliza: Usuario@Gmail.com → usuario@gmail.com
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)  # self.db → self._db (convención correcta)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, True, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, True, True, True, **extra_fields)

    def usuarios_sistema(self):
        return self.filter(
            is_active=True,        # solo usuarios activos
            is_superuser=False
        ).order_by('full_name')