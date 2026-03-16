from django import forms
from .models import User


class CSSMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('class', 'form-control')
            elif isinstance(widget, forms.DateInput):
                widget.attrs.setdefault('class', 'form-control')
                widget.attrs['type'] = 'date'
            elif isinstance(widget, forms.PasswordInput):
                widget.attrs.setdefault('class', 'form-control')
            else:
                widget.attrs.setdefault('class', 'form-control')


class LoginForm(CSSMixin, forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'usuario@correo.com'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    def clean(self):
        from django.contrib.auth import authenticate
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Correo o contraseña incorrectos.')
            if not user.is_active:
                raise forms.ValidationError('Este usuario está inactivo.')
        return cleaned


class UserRegisterForm(CSSMixin, forms.Form):
    email = forms.EmailField(label='Correo electrónico')
    full_name = forms.CharField(label='Nombre completo', max_length=100)
    occupation = forms.ChoiceField(label='Rol', choices=User.ROLE_CHOICES)
    genero = forms.ChoiceField(
        label='Género',
        choices=[('', 'Seleccionar')] + list(User.GENDER_CHOICES),
        required=False
    )
    date_birth = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    avatar = forms.ImageField(label='Avatar', required=False)
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned


class UpdatePasswordForm(CSSMixin, forms.Form):
    password1 = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    password3 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    def clean(self):
        cleaned = super().clean()
        p2 = cleaned.get('password2')
        p3 = cleaned.get('password3')
        if p2 and p3 and p2 != p3:
            raise forms.ValidationError('Las contraseñas nuevas no coinciden.')
        return cleaned
