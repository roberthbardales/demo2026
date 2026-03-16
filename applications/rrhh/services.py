from django.utils import timezone
from django.db import transaction
from .models import Ausencia, Vacaciones, Asistencia


class AusenciaService:

    @staticmethod
    @transaction.atomic
    def aprobar(ausencia, usuario):
        ausencia.estado = Ausencia.APROBADO
        ausencia.aprobado_por = usuario
        ausencia.save(update_fields=['estado', 'aprobado_por', 'modified'])
        return ausencia

    @staticmethod
    @transaction.atomic
    def rechazar(ausencia, usuario):
        ausencia.estado = Ausencia.RECHAZADO
        ausencia.aprobado_por = usuario
        ausencia.save(update_fields=['estado', 'aprobado_por', 'modified'])
        return ausencia


class VacacionesService:

    @staticmethod
    @transaction.atomic
    def aprobar(vacaciones, usuario):
        vacaciones.estado = Vacaciones.APROBADO
        vacaciones.aprobado_por = usuario
        vacaciones.save(update_fields=['estado', 'aprobado_por', 'modified'])
        return vacaciones

    @staticmethod
    @transaction.atomic
    def rechazar(vacaciones, usuario):
        vacaciones.estado = Vacaciones.RECHAZADO
        vacaciones.aprobado_por = usuario
        vacaciones.save(update_fields=['estado', 'aprobado_por', 'modified'])
        return vacaciones

    @staticmethod
    @transaction.atomic
    def marcar_gozado(vacaciones):
        vacaciones.estado = Vacaciones.GOZADO
        vacaciones.save(update_fields=['estado', 'modified'])
        return vacaciones


class AsistenciaService:

    @staticmethod
    @transaction.atomic
    def registrar_masivo(empleados, fecha, estado, registrado_por):
        """Registra asistencia para una lista de empleados en una fecha dada."""
        registros = []
        for empleado in empleados:
            obj, created = Asistencia.objects.get_or_create(
                empleado=empleado,
                fecha=fecha,
                defaults={
                    'estado': estado,
                    'registrado_por': registrado_por,
                }
            )
            registros.append(obj)
        return registros
