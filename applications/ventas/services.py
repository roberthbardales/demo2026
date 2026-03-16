from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Pedido, DetallePedido, Comprobante, DetalleComprobante


class PedidoService:

    @staticmethod
    @transaction.atomic
    def crear_pedido(cliente, vendedor, fecha, detalles, observaciones=''):
        """
        detalles: lista de dicts con keys: producto, cantidad, precio_unitario, descuento
        """
        # generar numero de pedido
        ultimo = Pedido.objects.order_by('-id').first()
        numero = f"PED-{str((ultimo.id if ultimo else 0) + 1).zfill(6)}"

        pedido = Pedido.objects.create(
            numero=numero,
            cliente=cliente,
            vendedor=vendedor,
            fecha=fecha,
            observaciones=observaciones,
            estado=Pedido.PENDIENTE,
        )

        for det in detalles:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=det['producto'],
                cantidad=det['cantidad'],
                precio_unitario=det['precio_unitario'],
                descuento=det.get('descuento', Decimal('0')),
            )

        pedido.calcular_totales()
        return pedido

    @staticmethod
    @transaction.atomic
    def confirmar_pedido(pedido):
        """Confirma el pedido y descuenta stock."""
        from applications.inventario.services import InventarioService
        from applications.inventario.models import Almacen

        almacen = Almacen.objects.filter(activo=True).first()
        if not almacen:
            raise ValueError("No hay almacenes activos configurados.")

        for detalle in pedido.detalles.select_related('producto'):
            if detalle.producto.stock_actual < detalle.cantidad:
                raise ValueError(
                    f"Stock insuficiente para '{detalle.producto.nombre}'. "
                    f"Disponible: {detalle.producto.stock_actual}"
                )

        for detalle in pedido.detalles.select_related('producto'):
            InventarioService.registrar_salida(
                producto=detalle.producto,
                almacen=almacen,
                cantidad=detalle.cantidad,
                usuario=pedido.vendedor,
                motivo=f"Venta - Pedido {pedido.numero}",
                documento=pedido.numero,
            )

        pedido.estado = Pedido.CONFIRMADO
        pedido.save(update_fields=['estado'])
        return pedido

    @staticmethod
    @transaction.atomic
    def anular_pedido(pedido):
        pedido.estado = Pedido.ANULADO
        pedido.save(update_fields=['estado'])
        return pedido


class ComprobanteService:

    SERIES = {
        Comprobante.FACTURA: 'F001',
        Comprobante.BOLETA: 'B001',
    }

    @staticmethod
    def siguiente_numero(tipo, serie):
        ultimo = Comprobante.objects.filter(
            tipo=tipo, serie=serie
        ).order_by('-numero').first()
        if ultimo:
            return str(int(ultimo.numero) + 1).zfill(8)
        return '00000001'

    @staticmethod
    @transaction.atomic
    def emitir_comprobante(pedido, tipo, fecha_emision, observaciones=''):
        """Emite un comprobante (factura o boleta) a partir de un pedido confirmado."""
        if pedido.estado != Pedido.CONFIRMADO:
            raise ValueError("Solo se pueden emitir comprobantes de pedidos confirmados.")

        if hasattr(pedido, 'comprobante'):
            raise ValueError("Este pedido ya tiene un comprobante emitido.")

        serie = ComprobanteService.SERIES[tipo]
        numero = ComprobanteService.siguiente_numero(tipo, serie)

        comprobante = Comprobante.objects.create(
            tipo=tipo,
            serie=serie,
            numero=numero,
            pedido=pedido,
            cliente=pedido.cliente,
            vendedor=pedido.vendedor,
            fecha_emision=fecha_emision,
            subtotal=pedido.subtotal,
            igv=pedido.igv,
            total=pedido.total,
            estado=Comprobante.EMITIDO,
            observaciones=observaciones,
        )

        for det in pedido.detalles.select_related('producto'):
            DetalleComprobante.objects.create(
                comprobante=comprobante,
                producto=det.producto,
                descripcion=det.producto.nombre,
                cantidad=det.cantidad,
                precio_unitario=det.precio_unitario,
                descuento=det.descuento,
                subtotal=det.subtotal,
            )

        pedido.estado = Pedido.ENTREGADO
        pedido.save(update_fields=['estado'])

        return comprobante

    @staticmethod
    @transaction.atomic
    def anular_comprobante(comprobante):
        comprobante.estado = Comprobante.ANULADO
        comprobante.save(update_fields=['estado'])
        return comprobante