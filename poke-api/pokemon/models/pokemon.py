from django.db import models
from .tipo import Tipo
from .movimiento import Movimiento


class Pokemon(models.Model):
    name = models.CharField(max_length=50)
    base_experience = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()
    sprite_front = models.URLField()
    sprite_back = models.URLField()
    tipos = models.ManyToManyField(Tipo)
    movimientos = models.ManyToManyField(Movimiento)
    hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    special_attack = models.IntegerField()
    special_defense = models.IntegerField()
    speed = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'pokemons'