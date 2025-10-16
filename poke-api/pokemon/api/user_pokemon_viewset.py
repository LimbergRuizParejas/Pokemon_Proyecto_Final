from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.models import UserPokemon


class UserPokemonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    class UserPokemonSerializer(serializers.ModelSerializer):
        pokemon_nombre = serializers.CharField(source='pokemon.name', read_only=True)
        pokemon_tipos = serializers.SerializerMethodField()
        pokemon_sprite_front = serializers.URLField(source='pokemon.sprite_front', read_only=True)
        pokemon_sprite_back = serializers.URLField(source='pokemon.sprite_back', read_only=True)
        pokemon_stats = serializers.SerializerMethodField()

        class Meta:
            model = UserPokemon
            fields = [
                'id', 'pokemon', 'pokemon_nombre', 'is_in_team', 'current_hp',
                'nivel', 'pokemon_tipos', 'pokemon_sprite_front', 'pokemon_sprite_back',
                'pokemon_stats'
            ]
            read_only_fields = ('user', 'current_hp', 'nivel')

        def get_pokemon_tipos(self, obj):
            return [tipo.name for tipo in obj.pokemon.tipos.all()]

        def get_pokemon_stats(self, obj):
            return {
                'hp': obj.pokemon.hp,
                'attack': obj.pokemon.attack,
                'defense': obj.pokemon.defense,
                'special_attack': obj.pokemon.special_attack,
                'special_defense': obj.pokemon.special_defense,
                'speed': obj.pokemon.speed
            }

    serializer_class = UserPokemonSerializer

    def get_queryset(self):
        return UserPokemon.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def equipo(self, request):
        """Obtiene solo los pokémones en el equipo de combate (máximo 6)"""
        equipo = self.get_queryset().filter(is_in_team=True)
        serializer = self.get_serializer(equipo, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reserva(self, request):
        """Obtiene pokémones en reserva"""
        reserva = self.get_queryset().filter(is_in_team=False)
        serializer = self.get_serializer(reserva, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_equipo(self, request, pk=None):
        """Cambia un pokémon entre equipo y reserva"""
        user_pokemon = self.get_object()

        if user_pokemon.is_in_team:
            user_pokemon.is_in_team = False
        else:
            equipo_count = self.get_queryset().filter(is_in_team=True).count()
            if equipo_count >= 6:
                return Response(
                    {"error": "Ya tienes 6 pokémones en tu equipo. Libera uno primero."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_pokemon.is_in_team = True

        user_pokemon.save()
        serializer = self.get_serializer(user_pokemon)
        return Response(serializer.data)