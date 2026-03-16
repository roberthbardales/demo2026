from django.db import models
from django.db.models import Q, Count
from django.utils import timezone


class EmpleadoQuerySet(models.QuerySet):

    def activos(self):
        return self.filter(estado='A')

    def por_departamento(self, departamento_id):
        return self.filter(cargo__departamento_id=departamento_id)

    def por_cargo(self, cargo_id):
        return self.filter(cargo_id=cargo_id)

    def buscar(self, termino):
        return self.filter(
            Q(nombres__icontains=termino) |
            Q(apellidos__icontains=termino) |
            Q(dni__icontains=termino) |
            Q(codigo__icontains=termino)
        )

    def con_contrato_vigente(self):
        return self.filter(contratos__estado='V').distinct()


class EmpleadoManager(models.Manager):

    def get_queryset(self):
        return EmpleadoQuerySet(self.model, using=self._db)

    def activos(self):
        return self.get_queryset().activos()

    def buscar(self, termino):
        return self.get_queryset().buscar(termino)

    def por_departamento(self, departamento_id):
        return self.get_queryset().por_departamento(departamento_id)


class AsistenciaQuerySet(models.QuerySet):

    def del_mes(self, year, month):
        return self.filter(fecha__year=year, fecha__month=month)

    def del_mes_actual(self):
        hoy = timezone.now()
        return self.del_mes(hoy.year, hoy.month)

    def por_empleado(self, empleado_id):
        return self.filter(empleado_id=empleado_id)

    def faltas(self):
        return self.filter(estado='F')

    def tardanzas(self):
        return self.filter(estado='T')


class AsistenciaManager(models.Manager):

    def get_queryset(self):
        return AsistenciaQuerySet(self.model, using=self._db)

    def del_mes_actual(self):
        return self.get_queryset().del_mes_actual()

    def por_empleado(self, empleado_id):
        return self.get_queryset().por_empleado(empleado_id)


class AusenciaManager(models.Manager):

    def pendientes(self):
        return self.filter(estado='P')

    def aprobadas(self):
        return self.filter(estado='A')

    def por_empleado(self, empleado_id):
        return self.filter(empleado_id=empleado_id)


class VacacionesManager(models.Manager):

    def pendientes(self):
        return self.filter(estado='P')

    def aprobadas(self):
        return self.filter(estado='A')

    def por_empleado(self, empleado_id):
        return self.filter(empleado_id=empleado_id)
