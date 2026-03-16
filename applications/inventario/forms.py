from django import forms
from .models import (
    Producto, Categoria, UnidadMedida, Almacen,
    Proveedor, Movimiento, AjusteInventario, Alerta
)


class CSSMixin:
    """Agrega clases Bootstrap a todos los campos."""
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
            else:
                widget.attrs.setdefault('class', 'form-control')


class CategoriaForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']


class UnidadMedidaForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = UnidadMedida
        fields = ['nombre', 'abreviatura', 'activo']


class AlmacenForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'ubicacion', 'responsable', 'activo']


class ProveedorForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'contacto', 'telefono', 'email', 'direccion', 'activo']


class ProductoForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion', 'categoria', 'unidad_medida',
            'proveedor', 'precio_compra', 'precio_venta',
            'stock_minimo', 'stock_maximo', 'imagen', 'activo'
        ]

    def clean(self):
        cleaned = super().clean()
        minimo = cleaned.get('stock_minimo')
        maximo = cleaned.get('stock_maximo')
        if minimo and maximo and minimo > maximo:
            raise forms.ValidationError("El stock mínimo no puede ser mayor al stock máximo.")
        return cleaned


class EntradaStockForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'almacen', 'cantidad', 'precio_unitario', 'motivo', 'documento_referencia']

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad


class SalidaStockForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'almacen', 'cantidad', 'motivo', 'documento_referencia']

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get('producto')
        cantidad = cleaned.get('cantidad')
        if producto and cantidad and producto.stock_actual < cantidad:
            raise forms.ValidationError(
                f"Stock insuficiente. Disponible: {producto.stock_actual}"
            )
        return cleaned


class AjusteInventarioForm(CSSMixin, forms.ModelForm):
    class Meta:
        model = AjusteInventario
        fields = ['producto', 'almacen', 'cantidad_nueva', 'motivo', 'observacion']

    def clean_cantidad_nueva(self):
        cantidad = self.cleaned_data.get('cantidad_nueva')
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError("La cantidad no puede ser negativa.")
        return cantidad


class FiltroMovimientoForm(CSSMixin, forms.Form):
    tipo = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Movimiento.TIPO_CHOICES),
        required=False
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.activos(),
        required=False,
        empty_label='Todos los productos'
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
