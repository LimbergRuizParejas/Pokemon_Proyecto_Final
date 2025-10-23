"""
Serializadores del módulo Pokémon
---------------------------------
Soporta tanto modelos con relaciones ForeignKey
como campos de texto plano para el tipo.
"""

from rest_framework import serializers
from pokemon.models import Pokemon, Tipo, Movimiento


# 🌿 TipoSerializer
class TipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo
        fields = ["id", "name"]
        read_only_fields = ["id"]


# ⚡ MovimientoSerializer
class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = ["id", "name", "power", "type"]
        read_only_fields = ["id"]


# 🧩 PokemonSerializer — robusto para ambos escenarios
class PokemonSerializer(serializers.ModelSerializer):
    """
    Serializa los datos de un Pokémon.
    Si el modelo tiene un campo ForeignKey 'tipo', lo serializa como objeto;
    si es texto plano, lo muestra directamente.
    """

    # Para casos con ForeignKey
    try:
        tipo = TipoSerializer(read_only=True)
    except Exception:
        tipo = serializers.CharField(read_only=True)

    movimientos = MovimientoSerializer(many=True, read_only=True)

    class Meta:
        model = Pokemon
        fields = [
            "id",
            "name",
            "hp",
            "attack",
            "defense",
            "tipo",        # 🔹 asegúrate de usar 'tipo' (no 'type')
            "movimientos",
            "image",
        ]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        """
        Personaliza la salida para mostrar los datos correctamente
        según el tipo de campo (relación o texto).
        """
        data = super().to_representation(instance)

        # Si el campo 'tipo' es texto, asegúrate de devolverlo simple
        tipo_value = getattr(instance, "tipo", None)
        if isinstance(tipo_value, str):
            data["tipo"] = tipo_value

        # Etiquetas más amigables
        data["hp_label"] = f"{instance.hp} HP"
        data["attack_label"] = f"{instance.attack} ATK"
        data["defense_label"] = f"{instance.defense} DEF"
        return data
