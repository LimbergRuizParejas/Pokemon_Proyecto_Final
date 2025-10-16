from django.db import models
from authentication.models import User
from .pokemon import Pokemon


class Batalla(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('ganada', 'Ganada'),
        ('perdida', 'Perdida'),
        ('escapada', 'Escapada'),
        ('capturado', 'Capturado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='batallas')
    pokemon_salvaje = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activa')
    pokebolas_restantes = models.IntegerField(default=5)
    curaciones_restantes = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batalla: {self.user.username} vs {self.pokemon_salvaje.name}"

    class Meta:
        db_table = 'batallas'