from django.db import models
from .tipo import Tipo


class Movimiento(models.Model):
    name = models.CharField(max_length=50, unique=True)
    power = models.IntegerField(null=True, blank=True)
    pp = models.IntegerField()
    accuracy = models.IntegerField(null=True, blank=True)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'movimientos'