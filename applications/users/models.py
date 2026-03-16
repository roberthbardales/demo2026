from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
#
from .managers import UserManager

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    # ROLES DEL SISTEMA
    ADMIN = '0'
    RRHH = '1'
    INVENTARIO = '2'
    EMPLEADO = '3'
    VENTAS = '4'          # ← NUEVO

    ROLE_CHOICES = (
        (ADMIN, 'Administrador'),
        (RRHH, 'RRHH'),
        (INVENTARIO, 'Inventario'),
        (EMPLEADO, 'Empleado'),
        (VENTAS, 'Ventas'),       # ← NUEVO
    )

    # GENEROS
    VARON = 'M'
    MUJER = 'F'
    OTRO = 'O'

    GENDER_CHOICES = (
        (VARON, 'Masculino'),
        (MUJER, 'Femenino'),
        (OTRO, 'Otros'),
    )

    email = models.EmailField(unique=True)

    full_name = models.CharField(
        'Nombres',
        max_length=100
    )

    occupation = models.CharField(
        'Rol',
        max_length=1,
        choices=ROLE_CHOICES,
        default=EMPLEADO
    )

    genero = models.CharField(
        'Genero',
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_birth = models.DateField(
        'Fecha de nacimiento',
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/',
        blank=True,
        null=True
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.email})"