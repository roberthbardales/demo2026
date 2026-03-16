from django.utils import timezone
from django.db import transaction
from .models import Producto, Movimiento, AjusteInventario, Alerta


class InventarioService:

    @staticmethod
    @transaction.atomic
    def registrar_entrada(producto, almacen, cantidad, precio_unitario, usuario, motivo='', documento=''):
        """Registra una entrada de stock y actualiza el producto."""
        movimiento = Movimiento.objects.create(
            tipo=Movimiento.ENTRADA,
            producto=producto,
            almacen=almacen,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            motivo=motivo,
            documento_referencia=documento,
            usuario=usuario,
        )
        producto.stock_actual = producto.stock_actual + cantidad
        producto.save(update_fields=['stock_actual', 'modified'])

        # resolver alertas de stock bajo si aplica
        if producto.stock_actual > producto.stock_minimo:
            Alerta.objects.filter(
                producto=producto,
                tipo__in=[Alerta.STOCK_BAJO, Alerta.SIN_STOCK],
                resuelta=False
            ).update(resuelta=True, fecha_resolucion=timezone.now())

        return movimiento

    @staticmethod
    @transaction.atomic
    def registrar_salida(producto, almacen, cantidad, usuario, motivo='', documento=''):
        """Registra una salida de stock y actualiza el producto."""
        if producto.stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {producto.stock_actual}")

        movimiento = Movimiento.objects.create(
            tipo=Movimiento.SALIDA,
            producto=producto,
            almacen=almacen,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            motivo=motivo,
            documento_referencia=documento,
            usuario=usuario,
        )
        producto.stock_actual = producto.stock_actual - cantidad
        producto.save(update_fields=['stock_actual', 'modified'])

        # generar alertas si corresponde
        AlertaService.verificar_stock(producto)

        return movimiento

    @staticmethod
    @transaction.atomic
    def ajustar_inventario(producto, almacen, cantidad_nueva, motivo, observacion, usuario):
        """Realiza un ajuste de inventario."""
        ajuste = AjusteInventario.objects.create(
            producto=producto,
            almacen=almacen,
            cantidad_anterior=producto.stock_actual,
            cantidad_nueva=cantidad_nueva,
            motivo=motivo,
            observacion=observacion,
            usuario=usuario,
        )
        producto.stock_actual = cantidad_nueva
        producto.save(update_fields=['stock_actual', 'modified'])
        AlertaService.verificar_stock(producto)
        return ajuste


class AlertaService:

    @staticmethod
    def verificar_stock(producto):
        """Verifica el stock y genera alertas si corresponde."""
        if producto.stock_actual == 0:
            Alerta.objects.get_or_create(
                producto=producto,
                tipo=Alerta.SIN_STOCK,
                resuelta=False,
                defaults={'mensaje': f"El producto '{producto.nombre}' no tiene stock disponible."}
            )
        elif producto.stock_actual <= producto.stock_minimo:
            Alerta.objects.get_or_create(
                producto=producto,
                tipo=Alerta.STOCK_BAJO,
                resuelta=False,
                defaults={'mensaje': f"El producto '{producto.nombre}' tiene stock bajo ({producto.stock_actual} {producto.unidad_medida.abreviatura})."}
            )
        elif producto.stock_maximo and producto.stock_actual > producto.stock_maximo:
            Alerta.objects.get_or_create(
                producto=producto,
                tipo=Alerta.STOCK_EXCESO,
                resuelta=False,
                defaults={'mensaje': f"El producto '{producto.nombre}' supera el stock máximo ({producto.stock_actual})."}
            )

    @staticmethod
    def resolver_alerta(alerta):
        alerta.resuelta = True
        alerta.fecha_resolucion = timezone.now()
        alerta.save(update_fields=['resuelta', 'fecha_resolucion'])

    @staticmethod
    def generar_alertas_masivas():
        """Recorre todos los productos activos y genera alertas."""
        from .models import Producto
        for producto in Producto.objects.activos():
            AlertaService.verificar_stock(producto)
