from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.models import Batalla, UserPokemon
from pokemon.services.pokeapi_service import PokeAPIService
from pokemon.services.combat_service import CombatService


class BatallaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    class BatallaSerializer(serializers.ModelSerializer):
        pokemon_salvaje_nombre = serializers.CharField(source='pokemon_salvaje.name', read_only=True)
        pokemon_salvaje_sprite = serializers.URLField(source='pokemon_salvaje.sprite_front', read_only=True)
        pokemon_salvaje_tipos = serializers.SerializerMethodField()
        pokemon_salvaje_hp_actual = serializers.SerializerMethodField()
        pokemon_salvaje_hp_max = serializers.IntegerField(source='pokemon_salvaje.hp', read_only=True)

        class Meta:
            model = Batalla
            fields = '__all__'
            read_only_fields = ('user', 'created_at')

        def get_pokemon_salvaje_tipos(self, obj):
            return [tipo.name for tipo in obj.pokemon_salvaje.tipos.all()]

        def get_pokemon_salvaje_hp_actual(self, obj):
            return obj.pokemon_salvaje.hp

    serializer_class = BatallaSerializer

    def get_queryset(self):
        return Batalla.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_aleatorio()

        if not pokemon_data:
            raise serializers.ValidationError("No se pudo obtener pokémon de la PokeAPI")

        pokemon_salvaje = service.guardar_pokemon_en_bd(pokemon_data)

        if not pokemon_salvaje:
            raise serializers.ValidationError("Error al guardar el pokémon salvaje")

        serializer.save(user=self.request.user, pokemon_salvaje=pokemon_salvaje)

    @action(detail=True, methods=['post'])
    def accion(self, request, pk=None):
        batalla = self.get_object()

        if batalla.estado != 'activa':
            return Response(
                {"error": "Esta batalla ya ha terminado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        accion = request.data.get('accion')
        user_pokemon_id = request.data.get('user_pokemon_id')
        movimiento_id = request.data.get('movimiento_id')

        try:
            user_pokemon = UserPokemon.objects.get(id=user_pokemon_id, user=request.user)
        except UserPokemon.DoesNotExist:
            return Response(
                {"error": "Pokémon no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        if accion == 'atacar':
            if not movimiento_id:
                return Response(
                    {"error": "Se requiere movimiento_id para atacar"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            resultado = CombatService.ejecutar_ataque(
                movimiento_id,
                user_pokemon,
                batalla.pokemon_salvaje
            )

            if 'error' in resultado:
                return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "accion": "atacar",
                "resultado": resultado,
                "batalla_id": batalla.id
            })

        return Response({
            "mensaje": f"Acción {accion} recibida (por implementar)",
            "batalla_id": batalla.id,
            "accion": accion
        })