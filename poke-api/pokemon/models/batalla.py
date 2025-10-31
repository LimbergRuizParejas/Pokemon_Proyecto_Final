from django.db import models
from authentication.models import User
from .pokemon import Pokemon
from .user_pokemon import UserPokemon


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

    hp_salvaje_actual = models.IntegerField(default=0)
    user_pokemon_actual = models.ForeignKey('UserPokemon', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batalla: {self.user.username} vs {self.pokemon_salvaje.name}"

    class Meta:
        db_table = 'batallas'

    def save(self, *args, **kwargs):
        if not self.pk and self.pokemon_salvaje:
            self.hp_salvaje_actual = self.pokemon_salvaje.hp
        super().save(*args, **kwargs)

    def obtener_pokemon_actual_usuario(self):
        if self.user_pokemon_actual and self.user_pokemon_actual.current_hp > 0:
            return self.user_pokemon_actual

        pokemon_vivo = UserPokemon.objects.filter(
            user=self.user,
            is_in_team=True,
            current_hp__gt=0
        ).first()

        if pokemon_vivo:
            self.user_pokemon_actual = pokemon_vivo
            self.save()

        return pokemon_vivo

    def verificar_fin_batalla(self):
        tiene_pokemones_vivos = UserPokemon.objects.filter(
            user=self.user,
            is_in_team=True,
            current_hp__gt=0
        ).exists()

        if not tiene_pokemones_vivos and self.estado == 'activa':
            self.estado = 'perdida'
            self.save()
            return True

        return False