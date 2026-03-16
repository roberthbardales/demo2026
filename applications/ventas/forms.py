from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Pedido, DetallePedido, Comprobante
from applications.inventario.models import Producto


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
            else:
                widget.attrs.setdefault('class', 'form-control')


class ClienteForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo', 'nombre', 'documento', 'email', 'telefono', 'direccion', 'activo']

    def clean_documento(self):
        doc = self.cleaned_data.get('documento')
        tipo = self.cleaned_data.get('tipo')
        if tipo == Cliente.NATURAL and len(doc) != 8:
            raise forms.ValidationError("El DNI debe tener 8 digitos.")
        if tipo == Cliente.JURIDICA and len(doc) != 11:
            raise forms.ValidationError("El RUC debe tener 11 digitos.")
        return doc


class PedidoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'fecha', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }


class DetallePedidoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario', 'descuento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.activos()
        self.fields['descuento'].initial = 0

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad


DetallePedidoFormSet = inlineformset_factory(
    Pedido,
    DetallePedido,
    form=DetallePedidoForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ComprobanteForm(CSSMixin, forms.Form):
    tipo = forms.ChoiceField(
        label='Tipo de Comprobante',
        choices=[
            (Comprobante.FACTURA, 'Factura'),
            (Comprobante.BOLETA, 'Boleta'),
        ]
    )
    fecha_emision = forms.DateField(
        label='Fecha de Emision',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    observaciones = forms.CharField(
        label='Observaciones',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )


class FiltroPedidoForm(CSSMixin, forms.Form):
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Pedido.ESTADO_CHOICES),
        required=False
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.activos(),
        required=False,
        empty_label='Todos los clientes'
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class FiltroComprobanteForm(CSSMixin, forms.Form):
    tipo = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Comprobante.TIPO_CHOICES),
        required=False
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.activos(),
        required=False,
        empty_label='Todos los clientes'
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )