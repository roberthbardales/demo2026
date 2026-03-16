from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


class ClienteQuerySet(models.QuerySet):

    def activos(self):
        return self.filter(activo=True)

    def buscar(self, termino):
        return self.filter(
            Q(nombre__icontains=termino) |
            Q(documento__icontains=termino)
        )

    def naturales(self):
        return self.filter(tipo='N')

    def juridicos(self):
        return self.filter(tipo='J')


class ClienteManager(models.Manager):

    def get_queryset(self):
        return ClienteQuerySet(self.model, using=self._db)

    def activos(self):
        return self.get_queryset().activos()

    def buscar(self, termino):
        return self.get_queryset().buscar(termino)


class PedidoQuerySet(models.QuerySet):

    def pendientes(self):
        return self.filter(estado='P')

    def confirmados(self):
        return self.filter(estado='C')

    def entregados(self):
        return self.filter(estado='E')

    def del_mes_actual(self):
        hoy = timezone.now()
        return self.filter(fecha__year=hoy.year, fecha__month=hoy.month)

    def por_cliente(self, cliente_id):
        return self.filter(cliente_id=cliente_id)

    def por_vendedor(self, vendedor_id):
        return self.filter(vendedor_id=vendedor_id)

    def total_ventas(self):
        return self.aggregate(total=Sum('total'))['total'] or 0


class PedidoManager(models.Manager):

    def get_queryset(self):
        return PedidoQuerySet(self.model, using=self._db)

    def pendientes(self):
        return self.get_queryset().pendientes()

    def del_mes_actual(self):
        return self.get_queryset().del_mes_actual()

    def total_ventas(self):
        return self.get_queryset().total_ventas()


class ComprobanteQuerySet(models.QuerySet):

    def emitidos(self):
        return self.filter(estado='E')

    def facturas(self):
        return self.filter(tipo='F')

    def boletas(self):
        return self.filter(tipo='B')

    def del_mes_actual(self):
        hoy = timezone.now()
        return self.filter(fecha_emision__year=hoy.year, fecha_emision__month=hoy.month)

    def por_cliente(self, cliente_id):
        return self.filter(cliente_id=cliente_id)


class ComprobanteManager(models.Manager):

    def get_queryset(self):
        return ComprobanteQuerySet(self.model, using=self._db)

    def emitidos(self):
        return self.get_queryset().emitidos()

    def del_mes_actual(self):
        return self.get_queryset().del_mes_actual()

    def facturas(self):
        return self.get_queryset().facturas()

    def boletas(self):
        return self.get_queryset().boletas()