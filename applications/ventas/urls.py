from django.urls import path
from . import views

app_name = 'ventas_app'

urlpatterns = [
    # Dashboard
    path('ventas/', views.DashboardView.as_view(), name='dashboard'),

    # Clientes
    path('ventas/clientes/', views.ClienteListView.as_view(), name='cliente-lista'),
    path('ventas/clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente-nuevo'),
    path('ventas/clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente-editar'),

    # Pedidos
    path('ventas/pedidos/', views.PedidoListView.as_view(), name='pedido-lista'),
    path('ventas/pedidos/nuevo/', views.PedidoCreateView.as_view(), name='pedido-nuevo'),
    path('ventas/pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido-detalle'),
    path('ventas/pedidos/<int:pk>/confirmar/', views.ConfirmarPedidoView.as_view(), name='pedido-confirmar'),
    path('ventas/pedidos/<int:pk>/anular/', views.AnularPedidoView.as_view(), name='pedido-anular'),

    # Comprobantes
    path('ventas/comprobantes/', views.ComprobanteListView.as_view(), name='comprobante-lista'),
    path('ventas/comprobantes/<int:pk>/', views.ComprobanteDetailView.as_view(), name='comprobante-detalle'),
    path('ventas/pedidos/<int:pk>/emitir/', views.EmitirComprobanteView.as_view(), name='comprobante-emitir'),
    path('ventas/comprobantes/<int:pk>/anular/', views.AnularComprobanteView.as_view(), name='comprobante-anular'),

    # Reportes
    path('ventas/reportes/pedidos/excel/', views.ReportePedidosExcelView.as_view(), name='reporte-pedidos-excel'),
    path('ventas/reportes/comprobantes/excel/', views.ReporteComprobantesExcelView.as_view(), name='reporte-comprobantes-excel'),
    path('ventas/comprobantes/<int:pk>/pdf/', views.ReporteComprobantePDFView.as_view(), name='comprobante-pdf'),
]