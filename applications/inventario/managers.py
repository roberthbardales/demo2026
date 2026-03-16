from django.db import models
from django.db.models import Sum, F, Q
from django.utils import timezone


class ProductoQuerySet(models.QuerySet):

    def activos(self):
        return self.filter(activo=True)

    def stock_bajo(self):
        return self.filter(activo=True, stock_actual__lte=F('stock_minimo'))

    def sin_stock(self):
        return self.filter(activo=True, stock_actual=0)

    def por_categoria(self, categoria_id):
        return self.filter(categoria_id=categoria_id, activo=True)

    def buscar(self, termino):
        return self.filter(
            Q(nombre__icontains=termino) |
            Q(codigo__icontains=termino) |
            Q(descripcion__icontains=termino)
        )

    def valor_total_inventario(self):
        return self.aggregate(
            total=Sum(F('stock_actual') * F('precio_compra'))
        )['total'] or 0


class ProductoManager(models.Manager):

    def get_queryset(self):
        return ProductoQuerySet(self.model, using=self._db)

    def activos(self):
        return self.get_queryset().activos()

    def stock_bajo(self):
        return self.get_queryset().stock_bajo()

    def sin_stock(self):
        return self.get_queryset().sin_stock()

    def buscar(self, termino):
        return self.get_queryset().buscar(termino)

    def valor_total_inventario(self):
        return self.get_queryset().valor_total_inventario()


class MovimientoQuerySet(models.QuerySet):

    def entradas(self):
        return self.filter(tipo='E')

    def salidas(self):
        return self.filter(tipo='S')

    def por_producto(self, producto_id):
        return self.filter(producto_id=producto_id)

    def por_almacen(self, almacen_id):
        return self.filter(almacen_id=almacen_id)

    def por_rango_fechas(self, fecha_inicio, fecha_fin):
        return self.filter(fecha__date__range=[fecha_inicio, fecha_fin])

    def del_mes_actual(self):
        hoy = timezone.now()
        return self.filter(fecha__year=hoy.year, fecha__month=hoy.month)


class MovimientoManager(models.Manager):

    def get_queryset(self):
        return MovimientoQuerySet(self.model, using=self._db)

    def entradas(self):
        return self.get_queryset().entradas()

    def salidas(self):
        return self.get_queryset().salidas()

    def del_mes_actual(self):
        return self.get_queryset().del_mes_actual()


class AlertaManager(models.Manager):

    def pendientes(self):
        return self.filter(resuelta=False)

    def resueltas(self):
        return self.filter(resuelta=True)

    def por_producto(self, producto_id):
        return self.filter(producto_id=producto_id, resuelta=False)
