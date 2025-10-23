# pokemon/models/pokemon.py

from django.db import models
from pokemon.models.tipo import Tipo


class Pokemon(models.Model):
    """
    Modelo principal que representa a un Pokémon dentro del sistema.
    Incluye estadísticas base, tipo y la imagen correspondiente.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Pokémon",
        help_text="Nombre único del Pokémon dentro del sistema."
    )

    hp = models.PositiveIntegerField(
        verbose_name="Puntos de salud (HP)",
        help_text="Cantidad de vida base del Pokémon."
    )

    attack = models.PositiveIntegerField(
        verbose_name="Ataque",
        help_text="Poder ofensivo del Pokémon."
    )

    defense = models.PositiveIntegerField(
        verbose_name="Defensa",
        help_text="Resistencia del Pokémon ante ataques."
    )

    image = models.URLField(
        max_length=300,
        verbose_name="Imagen del Pokémon",
        help_text="URL del sprite o imagen oficial del Pokémon."
    )

    tipo = models.ForeignKey(
        Tipo,
        on_delete=models.CASCADE,
        related_name="pokemons",
        verbose_name="Tipo principal",
        help_text="Tipo elemental al que pertenece este Pokémon (fuego, agua, etc.)."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        verbose_name = "Pokémon"
        verbose_name_plural = "Pokémon"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name.title()} ({self.tipo.name.title()})"

    # 🔹 Propiedad auxiliar para devolver el tipo como string simple
    @property
    def type(self):
        """
        Alias para acceder fácilmente al nombre del tipo (usado por el frontend).
        """
        return self.tipo.name if self.tipo else None

    # 🔹 Diccionario completo de estadísticas
    @property
    def full_stats(self):
        """
        Retorna un diccionario con las estadísticas completas del Pokémon.
        Ideal para APIs o serializaciones personalizadas.
        """
        total = self.hp + self.attack + self.defense
        return {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "total": total,
        }

    # 🔹 Cálculo de nivel de poder
    def power_index(self):
        """
        Calcula un índice de poder general del Pokémon (valor simbólico).
        Útil para rankings o comparaciones rápidas.
        """
        total = self.hp + self.attack + self.defense

        if total < 150:
            return "Débil ⚪"
        elif total < 250:
            return "Medio 🟡"
        else:
            return "Fuerte 🔴"
