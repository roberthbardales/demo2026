from django.contrib import admin
from .models import Cliente, Pedido, DetallePedido, Comprobante, DetalleComprobante


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


class DetalleComprobanteInline(admin.TabularInline):
    model = DetalleComprobante
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'documento', 'email', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'documento']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'vendedor', 'fecha', 'estado', 'total']
    list_filter = ['estado']
    search_fields = ['numero', 'cliente__nombre']
    inlines = [DetallePedidoInline]
    readonly_fields = ['subtotal', 'igv', 'total']


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'serie', 'numero', 'cliente', 'fecha_emision', 'total', 'estado']
    list_filter = ['tipo', 'estado']
    search_fields = ['numero', 'cliente__nombre']
    inlines = [DetalleComprobanteInline]
    readonly_fields = ['subtotal', 'igv', 'total']