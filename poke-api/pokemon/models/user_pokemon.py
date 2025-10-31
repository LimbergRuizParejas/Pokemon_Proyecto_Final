from django.db import models
from authentication.models import User
from .pokemon import Pokemon


class UserPokemon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_pokemones')
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    is_in_team = models.BooleanField(default=False)
    current_hp = models.IntegerField()
    nivel = models.IntegerField(default=5)
    experiencia = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_pokemones'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'pokemon'],
                name='unique_user_pokemon'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.pokemon.name}"