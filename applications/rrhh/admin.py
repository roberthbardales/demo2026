from django.contrib import admin
from .models import (
    Departamento, Cargo, Empleado, Contrato,
    Asistencia, Ausencia, Vacaciones, Documento
)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'departamento', 'activo']
    list_filter = ['activo', 'departamento']
    search_fields = ['nombre']


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'apellidos', 'nombres', 'cargo', 'fecha_ingreso', 'estado']
    list_filter = ['estado', 'cargo__departamento']
    search_fields = ['nombres', 'apellidos', 'dni', 'codigo']
    readonly_fields = ['created', 'modified']


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'sueldo', 'estado']
    list_filter = ['tipo', 'estado']
    search_fields = ['empleado__nombres', 'empleado__apellidos']


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha', 'hora_entrada', 'hora_salida', 'estado']
    list_filter = ['estado']
    search_fields = ['empleado__nombres', 'empleado__apellidos']


@admin.register(Ausencia)
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'estado']
    list_filter = ['tipo', 'estado']
    search_fields = ['empleado__nombres', 'empleado__apellidos']


@admin.register(Vacaciones)
class VacacionesAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado']
    list_filter = ['estado']
    search_fields = ['empleado__nombres', 'empleado__apellidos']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'tipo', 'nombre', 'fecha_emision', 'fecha_vencimiento']
    list_filter = ['tipo']
    search_fields = ['empleado__nombres', 'empleado__apellidos', 'nombre']
