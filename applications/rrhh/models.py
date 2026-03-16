from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel
from .managers import EmpleadoManager, AsistenciaManager, AusenciaManager, VacacionesManager

class Departamento(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = models.TextField('Descripción', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Cargo(TimeStampedModel):
    nombre = models.CharField('Nombre', max_length=100)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='cargos',
        verbose_name='Departamento'
    )
    descripcion = models.TextField('Descripción', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['departamento', 'nombre']

    def __str__(self):
        return f"{self.nombre} — {self.departamento}"


class Empleado(TimeStampedModel):
    ACTIVO = 'A'
    INACTIVO = 'I'
    VACACIONES = 'V'
    LICENCIA = 'L'
    ESTADO_CHOICES = (
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
        (VACACIONES, 'Vacaciones'),
        (LICENCIA, 'Licencia'),
    )

    VARON = 'M'
    MUJER = 'F'
    OTRO = 'O'
    GENERO_CHOICES = (
        (VARON, 'Masculino'),
        (MUJER, 'Femenino'),
        (OTRO, 'Otro'),
    )

    # Datos personales
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombres = models.CharField('Nombres', max_length=100)
    apellidos = models.CharField('Apellidos', max_length=100)
    dni = models.CharField('DNI', max_length=20, unique=True)
    genero = models.CharField('Género', max_length=1, choices=GENERO_CHOICES)
    fecha_nacimiento = models.DateField('Fecha Nacimiento', null=True, blank=True)
    email = models.EmailField('Email', blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.TextField('Dirección', blank=True)
    foto = models.ImageField('Foto', upload_to='empleados/fotos/', blank=True, null=True)

    # Datos laborales
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        related_name='empleados',
        verbose_name='Cargo'
    )
    fecha_ingreso = models.DateField('Fecha Ingreso')
    fecha_cese = models.DateField('Fecha Cese', null=True, blank=True)
    sueldo_base = models.DecimalField('Sueldo Base', max_digits=10, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=ACTIVO)

    # Vinculación con usuario del sistema (opcional)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='empleado',
        verbose_name='Usuario del sistema'
    )

    objects = EmpleadoManager()

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def departamento(self):
        return self.cargo.departamento


class Contrato(TimeStampedModel):
    INDEFINIDO = 'IND'
    PLAZO_FIJO = 'PF'
    PRACTICAS = 'PR'
    LOCACION = 'LOC'
    TIPO_CHOICES = (
        (INDEFINIDO, 'Indefinido'),
        (PLAZO_FIJO, 'Plazo Fijo'),
        (PRACTICAS, 'Prácticas'),
        (LOCACION, 'Locación de Servicios'),
    )

    VIGENTE = 'V'
    VENCIDO = 'X'
    RESCINDIDO = 'R'
    ESTADO_CHOICES = (
        (VIGENTE, 'Vigente'),
        (VENCIDO, 'Vencido'),
        (RESCINDIDO, 'Rescindido'),
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='contratos',
        verbose_name='Empleado'
    )
    tipo = models.CharField('Tipo', max_length=3, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField('Fecha Inicio')
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)
    sueldo = models.DecimalField('Sueldo', max_digits=10, decimal_places=2)
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=VIGENTE)
    archivo = models.FileField('Archivo', upload_to='contratos/', blank=True, null=True)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} — {self.get_tipo_display()} ({self.fecha_inicio})"


class Asistencia(TimeStampedModel):
    PRESENTE = 'P'
    TARDANZA = 'T'
    FALTA = 'F'
    JUSTIFICADO = 'J'
    ESTADO_CHOICES = (
        (PRESENTE, 'Presente'),
        (TARDANZA, 'Tardanza'),
        (FALTA, 'Falta'),
        (JUSTIFICADO, 'Justificado'),
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='asistencias',
        verbose_name='Empleado'
    )
    fecha = models.DateField('Fecha')
    hora_entrada = models.TimeField('Hora Entrada', null=True, blank=True)
    hora_salida = models.TimeField('Hora Salida', null=True, blank=True)
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=PRESENTE)
    observacion = models.CharField('Observación', max_length=200, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='asistencias_registradas'
    )

    objects = AsistenciaManager()

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-fecha', 'empleado']
        unique_together = [['empleado', 'fecha']]

    def __str__(self):
        return f"{self.empleado} — {self.fecha} ({self.get_estado_display()})"


class Ausencia(TimeStampedModel):
    ENFERMEDAD = 'ENF'
    PERSONAL = 'PER'
    FAMILIAR = 'FAM'
    CAPACITACION = 'CAP'
    OTRO = 'OTR'
    TIPO_CHOICES = (
        (ENFERMEDAD, 'Enfermedad'),
        (PERSONAL, 'Personal'),
        (FAMILIAR, 'Familiar'),
        (CAPACITACION, 'Capacitación'),
        (OTRO, 'Otro'),
    )

    PENDIENTE = 'P'
    APROBADO = 'A'
    RECHAZADO = 'R'
    ESTADO_CHOICES = (
        (PENDIENTE, 'Pendiente'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='ausencias',
        verbose_name='Empleado'
    )
    tipo = models.CharField('Tipo', max_length=3, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField('Fecha Inicio')
    fecha_fin = models.DateField('Fecha Fin')
    motivo = models.TextField('Motivo')
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=PENDIENTE)
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ausencias_aprobadas'
    )
    documento = models.FileField('Documento', upload_to='ausencias/', blank=True, null=True)

    objects = AusenciaManager()

    class Meta:
        verbose_name = 'Ausencia / Permiso'
        verbose_name_plural = 'Ausencias / Permisos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} — {self.get_tipo_display()} ({self.fecha_inicio})"

    @property
    def dias(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1


class Vacaciones(TimeStampedModel):
    PENDIENTE = 'P'
    APROBADO = 'A'
    RECHAZADO = 'R'
    GOZADO = 'G'
    ESTADO_CHOICES = (
        (PENDIENTE, 'Pendiente'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
        (GOZADO, 'Gozado'),
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='vacaciones',
        verbose_name='Empleado'
    )
    fecha_inicio = models.DateField('Fecha Inicio')
    fecha_fin = models.DateField('Fecha Fin')
    dias_solicitados = models.PositiveIntegerField('Días Solicitados')
    estado = models.CharField('Estado', max_length=1, choices=ESTADO_CHOICES, default=PENDIENTE)
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='vacaciones_aprobadas'
    )
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Vacaciones'
        verbose_name_plural = 'Vacaciones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} — {self.dias_solicitados} días ({self.fecha_inicio})"


class Documento(TimeStampedModel):
    DNI = 'DNI'
    CV = 'CV'
    CONTRATO = 'CON'
    CERTIFICADO = 'CER'
    TITULO = 'TIT'
    OTRO = 'OTR'
    TIPO_CHOICES = (
        (DNI, 'DNI'),
        (CV, 'Curriculum Vitae'),
        (CONTRATO, 'Contrato'),
        (CERTIFICADO, 'Certificado'),
        (TITULO, 'Título'),
        (OTRO, 'Otro'),
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='documentos',
        verbose_name='Empleado'
    )
    tipo = models.CharField('Tipo', max_length=3, choices=TIPO_CHOICES)
    nombre = models.CharField('Nombre', max_length=200)
    archivo = models.FileField('Archivo', upload_to='empleados/documentos/')
    fecha_emision = models.DateField('Fecha Emisión', null=True, blank=True)
    fecha_vencimiento = models.DateField('Fecha Vencimiento', null=True, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)

    objects = VacacionesManager()

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-created']

    def __str__(self):
        return f"{self.empleado} — {self.get_tipo_display()}: {self.nombre}"
