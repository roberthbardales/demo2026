from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movimiento, Producto
from .services import AlertaService


@receiver(post_save, sender=Movimiento)
def verificar_stock_tras_movimiento(sender, instance, created, **kwargs):
    """Verifica alertas de stock después de cada movimiento."""
    if created:
        AlertaService.verificar_stock(instance.producto)
