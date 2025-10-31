from rest_framework import serializers
from pokemon.models import Pokemon, UserPokemon, Movimiento, Tipo
from pokemon.services.pokeapi_service import PokeAPIService


class MovimientoSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source='tipo.name')

    class Meta:
        model = Movimiento
        fields = ['id', 'name', 'power', 'pp', 'accuracy', 'tipo']


class TipoDetalladoSerializer(serializers.Serializer):
    name = serializers.CharField()
    damage_relations = serializers.DictField()


class PokemonSerializer(serializers.ModelSerializer):
    tipos = serializers.SerializerMethodField()
    tipos_detallados = serializers.SerializerMethodField()
    relaciones_dano = serializers.SerializerMethodField()
    movimientos = MovimientoSerializer(many=True)
    sprites = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Pokemon
        fields = [
            'id', 'name', 'sprites', 'tipos', 'tipos_detallados',
            'relaciones_dano', 'stats', 'movimientos', 'height',
            'weight', 'base_experience'
        ]

    def get_sprites(self, obj):
        return {
            'front_default': obj.sprite_front,
            'back_default': obj.sprite_back
        }

    def get_tipos(self, obj):
        return [tipo.name for tipo in obj.tipos.all()]

    def get_tipos_detallados(self, obj):
        tipos_detallados = []
        for tipo in obj.tipos.all():
            tipos_detallados.append({
                'name': tipo.name,
                'damage_relations': tipo.damage_relations
            })
        return tipos_detallados

    def get_relaciones_dano(self, obj):
        service = PokeAPIService()
        tipos_info = self.get_tipos_detallados(obj)
        return service.calcular_debilidades_resistencias(tipos_info)

    def get_stats(self, obj):
        return {
            'hp': obj.hp,
            'attack': obj.attack,
            'defense': obj.defense,
            'special_attack': obj.special_attack,
            'special_defense': obj.special_defense,
            'speed': obj.speed
        }


class UserPokemonSerializer(serializers.ModelSerializer):
    pokemon = PokemonSerializer(read_only=True)
    user_pokemon_id = serializers.IntegerField(source='id')

    class Meta:
        model = UserPokemon
        fields = [
            'user_pokemon_id', 'pokemon', 'is_in_team', 'current_hp', 'nivel'
        ]