from django.contrib import admin
from .models import (
    UnidadMedida, Categoria, Almacen, Proveedor,
    Producto, Movimiento, AjusteInventario, Alerta
)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'responsable', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ruc', 'contacto', 'telefono', 'email', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'ruc']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'stock_actual', 'stock_minimo', 'activo']
    list_filter = ['activo', 'categoria']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['stock_actual', 'created', 'modified']


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'tipo', 'producto', 'almacen', 'cantidad', 'usuario']
    list_filter = ['tipo', 'almacen']
    search_fields = ['producto__nombre', 'producto__codigo']
    readonly_fields = ['fecha']


@admin.register(AjusteInventario)
class AjusteInventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'almacen', 'cantidad_anterior', 'cantidad_nueva', 'motivo', 'usuario']
    list_filter = ['motivo']
    readonly_fields = ['created']


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'resuelta', 'created']
    list_filter = ['tipo', 'resuelta']
    search_fields = ['producto__nombre']
