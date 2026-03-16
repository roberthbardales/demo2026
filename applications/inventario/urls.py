from django.urls import path
from . import views

app_name = 'inventario_app'

urlpatterns = [
    # Dashboard
    path('inventario/', views.DashboardView.as_view(), name='dashboard'),

    # Productos
    path('inventario/productos/', views.ProductoListView.as_view(), name='producto-lista'),
    path('inventario/productos/nuevo/', views.ProductoCreateView.as_view(), name='producto-nuevo'),
    path('inventario/productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto-detalle'),
    path('inventario/productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto-editar'),

    # Movimientos
    path('inventario/movimientos/', views.MovimientoListView.as_view(), name='movimiento-lista'),
    path('inventario/movimientos/entrada/', views.EntradaStockView.as_view(), name='entrada-stock'),
    path('inventario/movimientos/salida/', views.SalidaStockView.as_view(), name='salida-stock'),
    path('inventario/movimientos/ajuste/', views.AjusteInventarioView.as_view(), name='ajuste-inventario'),

    # Proveedores
    path('inventario/proveedores/', views.ProveedorListView.as_view(), name='proveedor-lista'),
    path('inventario/proveedores/nuevo/', views.ProveedorCreateView.as_view(), name='proveedor-nuevo'),
    path('inventario/proveedores/<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='proveedor-editar'),

    # Categorías
    path('inventario/categorias/', views.CategoriaListView.as_view(), name='categoria-lista'),
    path('inventario/categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria-nueva'),
    path('inventario/categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria-editar'),

    # Almacenes
    path('inventario/almacenes/', views.AlmacenListView.as_view(), name='almacen-lista'),
    path('inventario/almacenes/nuevo/', views.AlmacenCreateView.as_view(), name='almacen-nuevo'),
    path('inventario/almacenes/<int:pk>/editar/', views.AlmacenUpdateView.as_view(), name='almacen-editar'),

    # Alertas
    path('inventario/alertas/', views.AlertaListView.as_view(), name='alerta-lista'),

    # Reportes
    path('inventario/reportes/productos/excel/', views.ReporteProductosExcelView.as_view(), name='reporte-productos-excel'),
    path('inventario/reportes/productos/pdf/', views.ReporteProductosPDFView.as_view(), name='reporte-productos-pdf'),
    path('inventario/reportes/movimientos/excel/', views.ReporteMovimientosExcelView.as_view(), name='reporte-movimientos-excel'),
]
