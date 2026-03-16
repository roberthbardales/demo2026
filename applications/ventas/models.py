from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from .managers import ClienteManager, PedidoManager, ComprobanteManager


class Cliente(TimeStampedModel):
    NATURAL = 'N'
    JURIDICA = 'J'
    TIPO_CHOICES = (
        (NATURAL, 'Persona Natural'),
        (JURIDICA, 'Persona Juridica'),
    )

    tipo = models.CharField('Tipo', max_length=1, choices=TIPO_CHOICES, default=NATURAL)
    nombre = models.CharField('Nombre / Razon Social', max_length=200)
    documento = models.CharField('DNI / RUC', max_length=20, unique=True)
    email = models.EmailField('Email', blank=True)
    telefono = models.CharField('Telefono', max_length=20, blank=True)
    direccion = models.TextField('Direccion', blank=True)
    activo = models.BooleanField(default=True)

    objects = ClienteManager()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.documento})"


class Pedido(TimeStampedModel):
    PENDIENTE = 'P'
    CONFIRMADO = 'C'
    ENTREGADO = 'E'
    ANULADO = 'A'
    ESTADO_CHOICES = (
        (PENDIENTE, 'Pendiente'),
        (CONFIRMADO, 'Confirmado'),
        (ENTREGADO, 'Entregado'),
        (ANULADO, 'Anulado'),
    )

    numero = models.CharField('Numero', max_length=20, unique=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Cliente'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Vendedor'
    )
    fecha = models.DateField('Fecha')
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=PENDIENTE)
    observaciones = models.TextField('Observaciones', blank=True)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    igv = models.DecimalField('IGV (18%)', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)

    objects = PedidoManager()

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created']

    def __str__(self):
        return f"Pedido {self.numero} - {self.cliente}"

    def calcular_totales(self):
        from decimal import Decimal
        subtotal = sum(d.subtotal for d in self.detalles.all())
        igv = round(subtotal * Decimal('0.18'), 2)
        total = subtotal + igv
        self.subtotal = subtotal
        self.igv = igv
        self.total = total
        self.save(update_fields=['subtotal', 'igv', 'total'])


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Pedido'
    )
    producto = models.ForeignKey(
        'inventario.Producto',
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        verbose_name='Producto'
    )
    cantidad = models.DecimalField('Cantidad', max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=12, decimal_places=2)
    descuento = models.DecimalField('Descuento %', max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    @property
    def subtotal(self):
        from decimal import Decimal
        precio = self.precio_unitario * (1 - self.descuento / Decimal('100'))
        return round(precio * self.cantidad, 2)


class Comprobante(TimeStampedModel):
    FACTURA = 'F'
    BOLETA = 'B'
    TIPO_CHOICES = (
        (FACTURA, 'Factura'),
        (BOLETA, 'Boleta'),
    )

    EMITIDO = 'E'
    ANULADO = 'A'
    ESTADO_CHOICES = (
        (EMITIDO, 'Emitido'),
        (ANULADO, 'Anulado'),
    )

    tipo = models.CharField('Tipo', max_length=1, choices=TIPO_CHOICES)
    serie = models.CharField('Serie', max_length=4)
    numero = models.CharField('Numero', max_length=10)
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.PROTECT,
        related_name='comprobante',
        verbose_name='Pedido'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='comprobantes',
        verbose_name='Cliente'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='comprobantes',
        verbose_name='Vendedor'
    )
    fecha_emision = models.DateField('Fecha Emision')
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)
    igv = models.DecimalField('IGV', max_digits=12, decimal_places=2)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2)
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=EMITIDO)
    observaciones = models.TextField('Observaciones', blank=True)

    objects = ComprobanteManager()

    class Meta:
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        ordering = ['-created']
        unique_together = [['tipo', 'serie', 'numero']]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.serie}-{self.numero}"

    @property
    def numero_completo(self):
        return f"{self.serie}-{self.numero.zfill(8)}"


class DetalleComprobante(models.Model):
    comprobante = models.ForeignKey(
        Comprobante,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Comprobante'
    )
    producto = models.ForeignKey(
        'inventario.Producto',
        on_delete=models.PROTECT,
        related_name='detalles_comprobante',
        verbose_name='Producto'
    )
    descripcion = models.CharField('Descripcion', max_length=200)
    cantidad = models.DecimalField('Cantidad', max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=12, decimal_places=2)
    descuento = models.DecimalField('Descuento %', max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Comprobante'
        verbose_name_plural = 'Detalles de Comprobante'

    def __str__(self):
        return f"{self.descripcion} x {self.cantidad}"