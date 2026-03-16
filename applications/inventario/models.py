from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from .managers import ProductoManager, MovimientoManager, AlertaManager

class UnidadMedida(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    abreviatura = models.CharField('Abreviatura', max_length=10)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"


class Categoria(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Almacen(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100)
    ubicacion = models.CharField('Ubicación', max_length=200, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='almacenes',
        verbose_name='Responsable'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(TimeStampedModel):
    nombre = models.CharField('Nombre / Razón Social', max_length=200)
    ruc = models.CharField('RUC', max_length=20, unique=True, blank=True)
    contacto = models.CharField('Contacto', max_length=100, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    direccion = models.TextField('Dirección', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(TimeStampedModel):
    codigo = models.CharField('Código', max_length=50, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Categoría'
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Unidad de Medida'
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='productos',
        verbose_name='Proveedor'
    )
    precio_compra = models.DecimalField('Precio Compra', max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField('Precio Venta', max_digits=12, decimal_places=2, default=0)
    stock_actual = models.DecimalField('Stock Actual', max_digits=12, decimal_places=2, default=0)
    stock_minimo = models.DecimalField('Stock Mínimo', max_digits=12, decimal_places=2, default=0)
    stock_maximo = models.DecimalField('Stock Máximo', max_digits=12, decimal_places=2, default=0)
    imagen = models.ImageField('Imagen', upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    objects = ProductoManager()

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"

    @property
    def tiene_stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def valor_inventario(self):
        return self.stock_actual * self.precio_compra


class Movimiento(TimeStampedModel):
    ENTRADA = 'E'
    SALIDA = 'S'
    TIPO_CHOICES = (
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    )

    tipo = models.CharField('Tipo', max_length=1, choices=TIPO_CHOICES)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Producto'
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Almacén'
    )
    cantidad = models.DecimalField('Cantidad', max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=12, decimal_places=2, default=0)
    motivo = models.CharField('Motivo', max_length=200, blank=True)
    documento_referencia = models.CharField('Doc. Referencia', max_length=100, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Registrado por'
    )
    fecha = models.DateTimeField('Fecha', auto_now_add=True)

    objects = MovimientoManager()

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto} ({self.cantidad})"

    @property
    def total(self):
        return self.cantidad * self.precio_unitario


class AjusteInventario(TimeStampedModel):
    MOTIVO_CHOICES = (
        ('CONTEO', 'Conteo físico'),
        ('DANO', 'Producto dañado'),
        ('VENCIMIENTO', 'Vencimiento'),
        ('ROBO', 'Robo / Pérdida'),
        ('OTRO', 'Otro'),
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='ajustes',
        verbose_name='Producto'
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='ajustes',
        verbose_name='Almacén'
    )
    cantidad_anterior = models.DecimalField('Cantidad Anterior', max_digits=12, decimal_places=2)
    cantidad_nueva = models.DecimalField('Cantidad Nueva', max_digits=12, decimal_places=2)
    motivo = models.CharField('Motivo', max_length=20, choices=MOTIVO_CHOICES)
    observacion = models.TextField('Observación', blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ajustes',
        verbose_name='Realizado por'
    )

    class Meta:
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'
        ordering = ['-created']

    def __str__(self):
        return f"Ajuste {self.producto} — {self.created.date()}"

    @property
    def diferencia(self):
        return self.cantidad_nueva - self.cantidad_anterior


class Alerta(TimeStampedModel):
    STOCK_BAJO = 'STOCK_BAJO'
    SIN_STOCK = 'SIN_STOCK'
    STOCK_EXCESO = 'STOCK_EXCESO'
    TIPO_CHOICES = (
        (STOCK_BAJO, 'Stock Bajo'),
        (SIN_STOCK, 'Sin Stock'),
        (STOCK_EXCESO, 'Stock en Exceso'),
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name='Producto'
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField('Mensaje')
    resuelta = models.BooleanField('Resuelta', default=False)
    fecha_resolucion = models.DateTimeField('Fecha Resolución', null=True, blank=True)

    objects = AlertaManager()

    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.producto}"
