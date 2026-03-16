from django.urls import path
from . import views

app_name = 'rrhh_app'

urlpatterns = [
    # Dashboard
    path('rrhh/', views.DashboardView.as_view(), name='dashboard'),

    # Empleados
    path('rrhh/empleados/', views.EmpleadoListView.as_view(), name='empleado-lista'),
    path('rrhh/empleados/nuevo/', views.EmpleadoCreateView.as_view(), name='empleado-nuevo'),
    path('rrhh/empleados/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado-detalle'),
    path('rrhh/empleados/<int:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='empleado-editar'),

    # Contratos
    path('rrhh/contratos/', views.ContratoListView.as_view(), name='contrato-lista'),
    path('rrhh/contratos/nuevo/', views.ContratoCreateView.as_view(), name='contrato-nuevo'),
    path('rrhh/contratos/<int:pk>/editar/', views.ContratoUpdateView.as_view(), name='contrato-editar'),

    # Asistencia
    path('rrhh/asistencia/', views.AsistenciaListView.as_view(), name='asistencia-lista'),
    path('rrhh/asistencia/nueva/', views.AsistenciaCreateView.as_view(), name='asistencia-nueva'),

    # Ausencias
    path('rrhh/ausencias/', views.AusenciaListView.as_view(), name='ausencia-lista'),
    path('rrhh/ausencias/nueva/', views.AusenciaCreateView.as_view(), name='ausencia-nueva'),
    path('rrhh/ausencias/<int:pk>/aprobar/', views.AprobarAusenciaView.as_view(), name='ausencia-aprobar'),
    path('rrhh/ausencias/<int:pk>/rechazar/', views.RechazarAusenciaView.as_view(), name='ausencia-rechazar'),

    # Vacaciones
    path('rrhh/vacaciones/', views.VacacionesListView.as_view(), name='vacaciones-lista'),
    path('rrhh/vacaciones/nueva/', views.VacacionesCreateView.as_view(), name='vacaciones-nueva'),
    path('rrhh/vacaciones/<int:pk>/aprobar/', views.AprobarVacacionesView.as_view(), name='vacaciones-aprobar'),

    # Documentos
    path('rrhh/documentos/', views.DocumentoListView.as_view(), name='documento-lista'),
    path('rrhh/documentos/nuevo/', views.DocumentoCreateView.as_view(), name='documento-nuevo'),

    # Departamentos
    path('rrhh/departamentos/', views.DepartamentoListView.as_view(), name='departamento-lista'),
    path('rrhh/departamentos/nuevo/', views.DepartamentoCreateView.as_view(), name='departamento-nuevo'),

    # Cargos
    path('rrhh/cargos/', views.CargoListView.as_view(), name='cargo-lista'),
    path('rrhh/cargos/nuevo/', views.CargoCreateView.as_view(), name='cargo-nuevo'),

    # Reportes
    path('rrhh/reportes/empleados/excel/', views.ReporteEmpleadosExcelView.as_view(), name='reporte-empleados-excel'),
    path('rrhh/reportes/empleados/pdf/', views.ReporteEmpleadosPDFView.as_view(), name='reporte-empleados-pdf'),
    path('rrhh/reportes/asistencia/excel/', views.ReporteAsistenciaExcelView.as_view(), name='reporte-asistencia-excel'),
]
