from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Count, Q

from applications.users.mixins import InventarioMixin
from .models import (
    Producto, Categoria, UnidadMedida, Almacen,
    Proveedor, Movimiento, AjusteInventario, Alerta
)
from .forms import (
    ProductoForm, CategoriaForm, UnidadMedidaForm, AlmacenForm,
    ProveedorForm, EntradaStockForm, SalidaStockForm,
    AjusteInventarioForm, FiltroMovimientoForm
)
from .services import InventarioService
from .utils import (
    exportar_productos_excel, exportar_movimientos_excel,
    exportar_productos_pdf
)


# ─── DASHBOARD ───────────────────────────────────────────

class DashboardView(InventarioMixin, TemplateView):
    template_name = 'inventario/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_productos'] = Producto.objects.activos().count()
        ctx['productos_stock_bajo'] = Producto.objects.stock_bajo().count()
        ctx['productos_sin_stock'] = Producto.objects.sin_stock().count()
        ctx['total_proveedores'] = Proveedor.objects.filter(activo=True).count()
        ctx['alertas_pendientes'] = Alerta.objects.pendientes().count()
        ctx['movimientos_recientes'] = Movimiento.objects.select_related(
            'producto', 'almacen', 'usuario'
        )[:10]
        ctx['valor_inventario'] = Producto.objects.valor_total_inventario()
        ctx['alertas'] = Alerta.objects.pendientes().select_related('producto')[:5]
        return ctx


# ─── PRODUCTOS ───────────────────────────────────────────

class ProductoListView(InventarioMixin, ListView):
    template_name = 'inventario/producto_lista.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        qs = Producto.objects.activos().select_related('categoria', 'unidad_medida', 'proveedor')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('categoria')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
        if cat:
            qs = qs.filter(categoria_id=cat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categorias'] = Categoria.objects.filter(activo=True)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['categoria_sel'] = self.request.GET.get('categoria', '')
        return ctx


class ProductoDetailView(InventarioMixin, DetailView):
    model = Producto
    template_name = 'inventario/producto_detalle.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['movimientos'] = self.object.movimientos.select_related(
            'almacen', 'usuario'
        ).order_by('-fecha')[:20]
        ctx['alertas'] = self.object.alertas.filter(resuelta=False)
        return ctx


class ProductoCreateView(InventarioMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        messages.success(self.request, "Producto creado correctamente.")
        return super().form_valid(form)


class ProductoUpdateView(InventarioMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


# ─── MOVIMIENTOS ─────────────────────────────────────────

class MovimientoListView(InventarioMixin, ListView):
    template_name = 'inventario/movimiento_lista.html'
    context_object_name = 'movimientos'
    paginate_by = 25

    def get_queryset(self):
        qs = Movimiento.objects.select_related('producto', 'almacen', 'usuario').order_by('-fecha')
        form = FiltroMovimientoForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('tipo'):
                qs = qs.filter(tipo=form.cleaned_data['tipo'])
            if form.cleaned_data.get('producto'):
                qs = qs.filter(producto=form.cleaned_data['producto'])
            if form.cleaned_data.get('fecha_inicio'):
                qs = qs.filter(fecha__date__gte=form.cleaned_data['fecha_inicio'])
            if form.cleaned_data.get('fecha_fin'):
                qs = qs.filter(fecha__date__lte=form.cleaned_data['fecha_fin'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_filtro'] = FiltroMovimientoForm(self.request.GET)
        return ctx


class EntradaStockView(InventarioMixin, CreateView):
    form_class = EntradaStockForm
    template_name = 'inventario/entrada_form.html'
    success_url = reverse_lazy('inventario_app:movimiento-lista')

    def form_valid(self, form):
        cd = form.cleaned_data
        try:
            InventarioService.registrar_entrada(
                producto=cd['producto'],
                almacen=cd['almacen'],
                cantidad=cd['cantidad'],
                precio_unitario=cd['precio_unitario'],
                usuario=self.request.user,
                motivo=cd.get('motivo', ''),
                documento=cd.get('documento_referencia', ''),
            )
            messages.success(self.request, "Entrada de stock registrada correctamente.")
        except Exception as e:
            messages.error(self.request, str(e))
        return redirect(self.success_url)


class SalidaStockView(InventarioMixin, CreateView):
    form_class = SalidaStockForm
    template_name = 'inventario/salida_form.html'
    success_url = reverse_lazy('inventario_app:movimiento-lista')

    def form_valid(self, form):
        cd = form.cleaned_data
        try:
            InventarioService.registrar_salida(
                producto=cd['producto'],
                almacen=cd['almacen'],
                cantidad=cd['cantidad'],
                usuario=self.request.user,
                motivo=cd.get('motivo', ''),
                documento=cd.get('documento_referencia', ''),
            )
            messages.success(self.request, "Salida de stock registrada correctamente.")
        except ValueError as e:
            messages.error(self.request, str(e))
        return redirect(self.success_url)


class AjusteInventarioView(InventarioMixin, CreateView):
    form_class = AjusteInventarioForm
    template_name = 'inventario/ajuste_form.html'
    success_url = reverse_lazy('inventario_app:producto-lista')

    def form_valid(self, form):
        cd = form.cleaned_data
        InventarioService.ajustar_inventario(
            producto=cd['producto'],
            almacen=cd['almacen'],
            cantidad_nueva=cd['cantidad_nueva'],
            motivo=cd['motivo'],
            observacion=cd.get('observacion', ''),
            usuario=self.request.user,
        )
        messages.success(self.request, "Ajuste de inventario realizado correctamente.")
        return redirect(self.success_url)


# ─── PROVEEDORES ─────────────────────────────────────────

class ProveedorListView(InventarioMixin, ListView):
    model = Proveedor
    template_name = 'inventario/proveedor_lista.html'
    context_object_name = 'proveedores'
    paginate_by = 20

    def get_queryset(self):
        qs = Proveedor.objects.filter(activo=True)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(ruc__icontains=q))
        return qs


class ProveedorCreateView(InventarioMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedor_form.html'
    success_url = reverse_lazy('inventario_app:proveedor-lista')

    def form_valid(self, form):
        messages.success(self.request, "Proveedor creado correctamente.")
        return super().form_valid(form)


class ProveedorUpdateView(InventarioMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'inventario/proveedor_form.html'
    success_url = reverse_lazy('inventario_app:proveedor-lista')

    def form_valid(self, form):
        messages.success(self.request, "Proveedor actualizado correctamente.")
        return super().form_valid(form)


# ─── CATEGORÍAS ──────────────────────────────────────────

class CategoriaListView(InventarioMixin, ListView):
    model = Categoria
    template_name = 'inventario/categoria_lista.html'
    context_object_name = 'categorias'


class CategoriaCreateView(InventarioMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categoria_form.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')

    def form_valid(self, form):
        messages.success(self.request, "Categoría creada correctamente.")
        return super().form_valid(form)


class CategoriaUpdateView(InventarioMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventario/categoria_form.html'
    success_url = reverse_lazy('inventario_app:categoria-lista')


# ─── ALMACENES ───────────────────────────────────────────

class AlmacenListView(InventarioMixin, ListView):
    model = Almacen
    template_name = 'inventario/almacen_lista.html'
    context_object_name = 'almacenes'


class AlmacenCreateView(InventarioMixin, CreateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen_form.html'
    success_url = reverse_lazy('inventario_app:almacen-lista')

    def form_valid(self, form):
        messages.success(self.request, "Almacén creado correctamente.")
        return super().form_valid(form)


class AlmacenUpdateView(InventarioMixin, UpdateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = 'inventario/almacen_form.html'
    success_url = reverse_lazy('inventario_app:almacen-lista')


# ─── ALERTAS ─────────────────────────────────────────────

class AlertaListView(InventarioMixin, ListView):
    template_name = 'inventario/alerta_lista.html'
    context_object_name = 'alertas'

    def get_queryset(self):
        return Alerta.objects.pendientes().select_related('producto')


# ─── REPORTES ────────────────────────────────────────────

class ReporteProductosExcelView(InventarioMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Producto.objects.activos().select_related('categoria', 'unidad_medida', 'proveedor')
        return exportar_productos_excel(qs)


class ReporteProductosPDFView(InventarioMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Producto.objects.activos().select_related('categoria', 'unidad_medida', 'proveedor')
        return exportar_productos_pdf(qs)


class ReporteMovimientosExcelView(InventarioMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Movimiento.objects.select_related('producto', 'almacen', 'usuario').order_by('-fecha')
        return exportar_movimientos_excel(qs)
