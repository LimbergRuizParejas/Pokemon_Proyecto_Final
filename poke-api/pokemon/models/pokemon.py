from django.db import models
from authentication.models import User


class Tipo(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tipos'


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