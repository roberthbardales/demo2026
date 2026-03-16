from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum, Count, Q

from applications.users.mixins import VentasMixin
from .models import Cliente, Pedido, DetallePedido, Comprobante, DetalleComprobante
from .forms import (
    ClienteForm, PedidoForm, DetallePedidoFormSet,
    ComprobanteForm, FiltroPedidoForm, FiltroComprobanteForm
)
from .services import PedidoService, ComprobanteService
from .utils import (
    exportar_pedidos_excel, exportar_comprobantes_excel,
    exportar_comprobante_pdf
)


# ─── DASHBOARD ───────────────────────────────────────────

class DashboardView(VentasMixin, TemplateView):
    template_name = 'ventas/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.now()
        pedidos_mes = Pedido.objects.del_mes_actual()

        ctx['total_pedidos_mes'] = pedidos_mes.count()
        ctx['total_ventas_mes'] = pedidos_mes.filter(
            estado__in=[Pedido.CONFIRMADO, Pedido.ENTREGADO]
        ).aggregate(total=Sum('total'))['total'] or 0
        ctx['pedidos_pendientes'] = Pedido.objects.pendientes().count()
        ctx['total_clientes'] = Cliente.objects.activos().count()
        ctx['pedidos_recientes'] = Pedido.objects.select_related(
            'cliente', 'vendedor'
        ).order_by('-created')[:10]
        ctx['comprobantes_recientes'] = Comprobante.objects.emitidos().select_related(
            'cliente'
        ).order_by('-created')[:5]
        return ctx


# ─── CLIENTES ────────────────────────────────────────────

class ClienteListView(VentasMixin, ListView):
    template_name = 'ventas/cliente_lista.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        qs = Cliente.objects.activos()
        q = self.request.GET.get('q')
        if q:
            qs = qs.buscar(q)
        return qs


class ClienteCreateView(VentasMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ventas/cliente_form.html'
    success_url = reverse_lazy('ventas_app:cliente-lista')

    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado correctamente.")
        return super().form_valid(form)


class ClienteUpdateView(VentasMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ventas/cliente_form.html'
    success_url = reverse_lazy('ventas_app:cliente-lista')

    def form_valid(self, form):
        messages.success(self.request, "Cliente actualizado correctamente.")
        return super().form_valid(form)


# ─── PEDIDOS ─────────────────────────────────────────────

class PedidoListView(VentasMixin, ListView):
    template_name = 'ventas/pedido_lista.html'
    context_object_name = 'pedidos'
    paginate_by = 20

    def get_queryset(self):
        qs = Pedido.objects.select_related('cliente', 'vendedor').order_by('-created')
        form = FiltroPedidoForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('estado'):
                qs = qs.filter(estado=form.cleaned_data['estado'])
            if form.cleaned_data.get('cliente'):
                qs = qs.filter(cliente=form.cleaned_data['cliente'])
            if form.cleaned_data.get('fecha_inicio'):
                qs = qs.filter(fecha__gte=form.cleaned_data['fecha_inicio'])
            if form.cleaned_data.get('fecha_fin'):
                qs = qs.filter(fecha__lte=form.cleaned_data['fecha_fin'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_filtro'] = FiltroPedidoForm(self.request.GET)
        return ctx


class PedidoDetailView(VentasMixin, DetailView):
    model = Pedido
    template_name = 'ventas/pedido_detalle.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['detalles'] = self.object.detalles.select_related('producto')
        ctx['tiene_comprobante'] = hasattr(self.object, 'comprobante')
        ctx['form_comprobante'] = ComprobanteForm()
        return ctx


class PedidoCreateView(VentasMixin, TemplateView):
    template_name = 'ventas/pedido_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = PedidoForm()
        ctx['formset'] = DetallePedidoFormSet()
        return ctx

    def post(self, request, *args, **kwargs):
        form = PedidoForm(request.POST)
        formset = DetallePedidoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            detalles = []
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE'):
                    detalles.append({
                        'producto': f.cleaned_data['producto'],
                        'cantidad': f.cleaned_data['cantidad'],
                        'precio_unitario': f.cleaned_data['precio_unitario'],
                        'descuento': f.cleaned_data.get('descuento', 0),
                    })

            if not detalles:
                messages.error(request, "Debe agregar al menos un producto.")
                return self.render_to_response({'form': form, 'formset': formset})

            try:
                pedido = PedidoService.crear_pedido(
                    cliente=form.cleaned_data['cliente'],
                    vendedor=request.user,
                    fecha=form.cleaned_data['fecha'],
                    detalles=detalles,
                    observaciones=form.cleaned_data.get('observaciones', ''),
                )
                messages.success(request, f"Pedido {pedido.numero} creado correctamente.")
                return redirect('ventas_app:pedido-detalle', pk=pedido.pk)
            except Exception as e:
                messages.error(request, str(e))

        return self.render_to_response({'form': form, 'formset': formset})


class ConfirmarPedidoView(VentasMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        try:
            PedidoService.confirmar_pedido(pedido)
            messages.success(request, f"Pedido {pedido.numero} confirmado. Stock descontado.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('ventas_app:pedido-detalle', pk=pedido.pk)


class AnularPedidoView(VentasMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        PedidoService.anular_pedido(pedido)
        messages.warning(request, f"Pedido {pedido.numero} anulado.")
        return redirect('ventas_app:pedido-lista')


# ─── COMPROBANTES ────────────────────────────────────────

class ComprobanteListView(VentasMixin, ListView):
    template_name = 'ventas/comprobante_lista.html'
    context_object_name = 'comprobantes'
    paginate_by = 20

    def get_queryset(self):
        qs = Comprobante.objects.select_related('cliente', 'vendedor').order_by('-created')
        form = FiltroComprobanteForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('tipo'):
                qs = qs.filter(tipo=form.cleaned_data['tipo'])
            if form.cleaned_data.get('cliente'):
                qs = qs.filter(cliente=form.cleaned_data['cliente'])
            if form.cleaned_data.get('fecha_inicio'):
                qs = qs.filter(fecha_emision__gte=form.cleaned_data['fecha_inicio'])
            if form.cleaned_data.get('fecha_fin'):
                qs = qs.filter(fecha_emision__lte=form.cleaned_data['fecha_fin'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_filtro'] = FiltroComprobanteForm(self.request.GET)
        return ctx


class ComprobanteDetailView(VentasMixin, DetailView):
    model = Comprobante
    template_name = 'ventas/comprobante_detalle.html'
    context_object_name = 'comprobante'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['detalles'] = self.object.detalles.select_related('producto')
        return ctx


class EmitirComprobanteView(VentasMixin, TemplateView):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        form = ComprobanteForm(request.POST)
        if form.is_valid():
            try:
                comprobante = ComprobanteService.emitir_comprobante(
                    pedido=pedido,
                    tipo=form.cleaned_data['tipo'],
                    fecha_emision=form.cleaned_data['fecha_emision'],
                    observaciones=form.cleaned_data.get('observaciones', ''),
                )
                messages.success(request, f"{comprobante} emitido correctamente.")
                return redirect('ventas_app:comprobante-detalle', pk=comprobante.pk)
            except ValueError as e:
                messages.error(request, str(e))
        return redirect('ventas_app:pedido-detalle', pk=pedido.pk)


class AnularComprobanteView(VentasMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        comprobante = get_object_or_404(Comprobante, pk=pk)
        ComprobanteService.anular_comprobante(comprobante)
        messages.warning(request, f"{comprobante} anulado.")
        return redirect('ventas_app:comprobante-lista')


# ─── REPORTES ────────────────────────────────────────────

class ReportePedidosExcelView(VentasMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Pedido.objects.select_related('cliente', 'vendedor').order_by('-created')
        return exportar_pedidos_excel(qs)


class ReporteComprobantesExcelView(VentasMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Comprobante.objects.emitidos().select_related('cliente', 'vendedor')
        return exportar_comprobantes_excel(qs)


class ReporteComprobantePDFView(VentasMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        comprobante = get_object_or_404(Comprobante, pk=pk)
        return exportar_comprobante_pdf(comprobante)