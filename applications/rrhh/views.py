from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from applications.users.mixins import RRHHMixin
from .models import (
    Departamento, Cargo, Empleado, Contrato,
    Asistencia, Ausencia, Vacaciones, Documento
)
from .forms import (
    DepartamentoForm, CargoForm, EmpleadoForm, ContratoForm,
    AsistenciaForm, AusenciaForm, VacacionesForm, DocumentoForm,
    FiltroAsistenciaForm
)
from .services import AusenciaService, VacacionesService
from .utils import (
    exportar_empleados_excel, exportar_empleados_pdf,
    exportar_asistencia_excel
)


# ─── DASHBOARD ───────────────────────────────────────────

class DashboardView(RRHHMixin, TemplateView):
    template_name = 'rrhh/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_empleados'] = Empleado.objects.activos().count()
        ctx['total_departamentos'] = Departamento.objects.filter(activo=True).count()
        ctx['ausencias_pendientes'] = Ausencia.objects.filter(estado='P').count()
        ctx['vacaciones_pendientes'] = Vacaciones.objects.filter(estado='P').count()
        ctx['contratos_vigentes'] = Contrato.objects.filter(estado='V').count()
        ctx['empleados_recientes'] = Empleado.objects.activos().select_related(
            'cargo__departamento'
        ).order_by('-fecha_ingreso')[:5]
        ctx['ausencias_recientes'] = Ausencia.objects.filter(
            estado='P'
        ).select_related('empleado')[:5]
        return ctx


# ─── EMPLEADOS ───────────────────────────────────────────

class EmpleadoListView(RRHHMixin, ListView):
    template_name = 'rrhh/empleado_lista.html'
    context_object_name = 'empleados'
    paginate_by = 20

    def get_queryset(self):
        qs = Empleado.objects.activos().select_related('cargo__departamento')
        q = self.request.GET.get('q')
        dep = self.request.GET.get('departamento')
        if q:
            qs = qs.buscar(q)
        if dep:
            qs = qs.por_departamento(dep)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departamentos'] = Departamento.objects.filter(activo=True)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['dep_sel'] = self.request.GET.get('departamento', '')
        return ctx


class EmpleadoDetailView(RRHHMixin, DetailView):
    model = Empleado
    template_name = 'rrhh/empleado_detalle.html'
    context_object_name = 'empleado'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['contratos'] = self.object.contratos.order_by('-fecha_inicio')
        ctx['asistencias'] = self.object.asistencias.order_by('-fecha')[:30]
        ctx['ausencias'] = self.object.ausencias.order_by('-fecha_inicio')[:10]
        ctx['vacaciones'] = self.object.vacaciones.order_by('-fecha_inicio')[:10]
        ctx['documentos'] = self.object.documentos.order_by('-created')
        return ctx


class EmpleadoCreateView(RRHHMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'rrhh/empleado_form.html'
    success_url = reverse_lazy('rrhh_app:empleado-lista')

    def form_valid(self, form):
        messages.success(self.request, "Empleado registrado correctamente.")
        return super().form_valid(form)


class EmpleadoUpdateView(RRHHMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'rrhh/empleado_form.html'
    success_url = reverse_lazy('rrhh_app:empleado-lista')

    def form_valid(self, form):
        messages.success(self.request, "Empleado actualizado correctamente.")
        return super().form_valid(form)


# ─── CONTRATOS ───────────────────────────────────────────

class ContratoListView(RRHHMixin, ListView):
    model = Contrato
    template_name = 'rrhh/contrato_lista.html'
    context_object_name = 'contratos'
    paginate_by = 20

    def get_queryset(self):
        return Contrato.objects.select_related('empleado').order_by('-fecha_inicio')


class ContratoCreateView(RRHHMixin, CreateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'rrhh/contrato_form.html'
    success_url = reverse_lazy('rrhh_app:contrato-lista')

    def form_valid(self, form):
        messages.success(self.request, "Contrato registrado correctamente.")
        return super().form_valid(form)


class ContratoUpdateView(RRHHMixin, UpdateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'rrhh/contrato_form.html'
    success_url = reverse_lazy('rrhh_app:contrato-lista')


# ─── ASISTENCIA ──────────────────────────────────────────

class AsistenciaListView(RRHHMixin, ListView):
    template_name = 'rrhh/asistencia_lista.html'
    context_object_name = 'asistencias'
    paginate_by = 30

    def get_queryset(self):
        qs = Asistencia.objects.select_related('empleado').order_by('-fecha')
        form = FiltroAsistenciaForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('empleado'):
                qs = qs.filter(empleado=form.cleaned_data['empleado'])
            if form.cleaned_data.get('mes'):
                qs = qs.filter(fecha__month=form.cleaned_data['mes'])
            if form.cleaned_data.get('anio'):
                qs = qs.filter(fecha__year=form.cleaned_data['anio'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_filtro'] = FiltroAsistenciaForm(self.request.GET)
        return ctx


class AsistenciaCreateView(RRHHMixin, CreateView):
    model = Asistencia
    form_class = AsistenciaForm
    template_name = 'rrhh/asistencia_form.html'
    success_url = reverse_lazy('rrhh_app:asistencia-lista')

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        messages.success(self.request, "Asistencia registrada correctamente.")
        return super().form_valid(form)


# ─── AUSENCIAS ───────────────────────────────────────────

class AusenciaListView(RRHHMixin, ListView):
    model = Ausencia
    template_name = 'rrhh/ausencia_lista.html'
    context_object_name = 'ausencias'
    paginate_by = 20

    def get_queryset(self):
        return Ausencia.objects.select_related('empleado').order_by('-fecha_inicio')


class AusenciaCreateView(RRHHMixin, CreateView):
    model = Ausencia
    form_class = AusenciaForm
    template_name = 'rrhh/ausencia_form.html'
    success_url = reverse_lazy('rrhh_app:ausencia-lista')

    def form_valid(self, form):
        messages.success(self.request, "Ausencia registrada correctamente.")
        return super().form_valid(form)


class AprobarAusenciaView(RRHHMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        ausencia = get_object_or_404(Ausencia, pk=pk)
        AusenciaService.aprobar(ausencia, request.user)
        messages.success(request, "Ausencia aprobada.")
        return redirect('rrhh_app:ausencia-lista')


class RechazarAusenciaView(RRHHMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        ausencia = get_object_or_404(Ausencia, pk=pk)
        AusenciaService.rechazar(ausencia, request.user)
        messages.warning(request, "Ausencia rechazada.")
        return redirect('rrhh_app:ausencia-lista')


# ─── VACACIONES ──────────────────────────────────────────

class VacacionesListView(RRHHMixin, ListView):
    model = Vacaciones
    template_name = 'rrhh/vacaciones_lista.html'
    context_object_name = 'vacaciones'
    paginate_by = 20

    def get_queryset(self):
        return Vacaciones.objects.select_related('empleado').order_by('-fecha_inicio')


class VacacionesCreateView(RRHHMixin, CreateView):
    model = Vacaciones
    form_class = VacacionesForm
    template_name = 'rrhh/vacaciones_form.html'
    success_url = reverse_lazy('rrhh_app:vacaciones-lista')

    def form_valid(self, form):
        messages.success(self.request, "Solicitud de vacaciones registrada.")
        return super().form_valid(form)


class AprobarVacacionesView(RRHHMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        vac = get_object_or_404(Vacaciones, pk=pk)
        VacacionesService.aprobar(vac, request.user)
        messages.success(request, "Vacaciones aprobadas.")
        return redirect('rrhh_app:vacaciones-lista')


# ─── DOCUMENTOS ──────────────────────────────────────────

class DocumentoListView(RRHHMixin, ListView):
    model = Documento
    template_name = 'rrhh/documento_lista.html'
    context_object_name = 'documentos'
    paginate_by = 20

    def get_queryset(self):
        return Documento.objects.select_related('empleado').order_by('-created')


class DocumentoCreateView(RRHHMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'rrhh/documento_form.html'
    success_url = reverse_lazy('rrhh_app:documento-lista')

    def form_valid(self, form):
        messages.success(self.request, "Documento cargado correctamente.")
        return super().form_valid(form)


# ─── DEPARTAMENTOS / CARGOS ──────────────────────────────

class DepartamentoListView(RRHHMixin, ListView):
    model = Departamento
    template_name = 'rrhh/departamento_lista.html'
    context_object_name = 'departamentos'


class DepartamentoCreateView(RRHHMixin, CreateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'rrhh/departamento_form.html'
    success_url = reverse_lazy('rrhh_app:departamento-lista')

    def form_valid(self, form):
        messages.success(self.request, "Departamento creado correctamente.")
        return super().form_valid(form)


class CargoListView(RRHHMixin, ListView):
    model = Cargo
    template_name = 'rrhh/cargo_lista.html'
    context_object_name = 'cargos'

    def get_queryset(self):
        return Cargo.objects.select_related('departamento').filter(activo=True)


class CargoCreateView(RRHHMixin, CreateView):
    model = Cargo
    form_class = CargoForm
    template_name = 'rrhh/cargo_form.html'
    success_url = reverse_lazy('rrhh_app:cargo-lista')

    def form_valid(self, form):
        messages.success(self.request, "Cargo creado correctamente.")
        return super().form_valid(form)


# ─── REPORTES ────────────────────────────────────────────

class ReporteEmpleadosExcelView(RRHHMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Empleado.objects.activos().select_related('cargo__departamento')
        return exportar_empleados_excel(qs)


class ReporteEmpleadosPDFView(RRHHMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Empleado.objects.activos().select_related('cargo__departamento')
        return exportar_empleados_pdf(qs)


class ReporteAsistenciaExcelView(RRHHMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        qs = Asistencia.objects.del_mes_actual().select_related('empleado')
        return exportar_asistencia_excel(qs)
