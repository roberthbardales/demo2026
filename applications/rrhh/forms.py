from django import forms
from .models import (
    Departamento, Cargo, Empleado, Contrato,
    Asistencia, Ausencia, Vacaciones, Documento
)


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
                widget.attrs.setdefault('rows', 3)
            elif isinstance(widget, forms.DateInput):
                widget.attrs.setdefault('class', 'form-control')
                widget.attrs['type'] = 'date'
            elif isinstance(widget, forms.TimeInput):
                widget.attrs.setdefault('class', 'form-control')
                widget.attrs['type'] = 'time'
            else:
                widget.attrs.setdefault('class', 'form-control')


class DepartamentoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'descripcion', 'activo']


class CargoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nombre', 'departamento', 'descripcion', 'activo']


class EmpleadoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'codigo', 'nombres', 'apellidos', 'dni', 'genero',
            'fecha_nacimiento', 'email', 'telefono', 'direccion', 'foto',
            'cargo', 'fecha_ingreso', 'sueldo_base', 'estado', 'usuario'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }


class ContratoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'sueldo', 'estado', 'archivo', 'observaciones']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin = cleaned.get('fecha_fin')
        if inicio and fin and fin < inicio:
            raise forms.ValidationError("La fecha fin no puede ser anterior a la fecha inicio.")
        return cleaned


class AsistenciaForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['empleado', 'fecha', 'hora_entrada', 'hora_salida', 'estado', 'observacion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }


class AusenciaForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Ausencia
        fields = ['empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'motivo', 'documento']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin = cleaned.get('fecha_fin')
        if inicio and fin and fin < inicio:
            raise forms.ValidationError("La fecha fin no puede ser anterior a la fecha inicio.")
        return cleaned


class VacacionesForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Vacaciones
        fields = ['empleado', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'observaciones']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class DocumentoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['empleado', 'tipo', 'nombre', 'archivo', 'fecha_emision', 'fecha_vencimiento', 'observaciones']
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }


class FiltroAsistenciaForm(CSSMixin, forms.Form):
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.activos(),
        required=False,
        empty_label='Todos los empleados'
    )
    mes = forms.IntegerField(
        min_value=1, max_value=12,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    anio = forms.IntegerField(
        min_value=2020,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
