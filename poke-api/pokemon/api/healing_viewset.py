from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.services.healing_service import HealingService
from .serializers import UserPokemonSerializer
from django.db import models


class HealingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def curar_todos(self, request):
        """Cura todos los Pokémon del usuario (restaura HP al máximo)"""
        try:
            cantidad_curados = HealingService.curar_todos_los_pokemon(request.user)

            return Response({
                "mensaje": f"¡Todos tus Pokémon han sido curados!",
                "pokemon_curados": cantidad_curados
            })
        except Exception as e:
            return Response(
                {"error": f"Error al curar Pokémon: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def curar(self, request):
        """Cura un Pokémon específico"""
        user_pokemon_id = request.data.get('user_pokemon_id')

        if not user_pokemon_id:
            return Response(
                {"error": "Se requiere user_pokemon_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_pokemon = HealingService.curar_pokemon_especifico(request.user, user_pokemon_id)

            if not user_pokemon:
                return Response(
                    {"error": "Pokémon no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = UserPokemonSerializer(user_pokemon)

            return Response({
                "mensaje": f"¡{user_pokemon.pokemon.name} ha sido curado!",
                "pokemon": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": f"Error al curar Pokémon: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def revivir_todos(self, request):
        """Revive todos los Pokémon derrotados del usuario"""
        try:
            cantidad_revividos = HealingService.revivir_todos_los_pokemon(request.user)

            return Response({
                "mensaje": f"¡Has revivido a {cantidad_revividos} Pokémon!",
                "pokemon_revividos": cantidad_revividos
            })
        except Exception as e:
            return Response(
                {"error": f"Error al revivir Pokémon: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def revivir(self, request):
        """Revive un Pokémon específico"""
        user_pokemon_id = request.data.get('user_pokemon_id')

        if not user_pokemon_id:
            return Response(
                {"error": "Se requiere user_pokemon_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_pokemon = HealingService.revivir_pokemon(request.user, user_pokemon_id)

            if not user_pokemon:
                return Response(
                    {"error": "Pokémon no encontrado"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = UserPokemonSerializer(user_pokemon)

            return Response({
                "mensaje": f"¡{user_pokemon.pokemon.name} ha sido revivido!",
                "pokemon": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": f"Error al revivir Pokémon: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def estado(self, request):
        """Muestra el estado actual de los Pokémon (para ver cuáles necesitan curación)"""
        from pokemon.models import UserPokemon

        pokemones = UserPokemon.objects.filter(user=request.user)

        estadisticas = {
            "total_pokemon": pokemones.count(),
            "pokemon_sanos": pokemones.filter(current_hp__gt=0).count(),
            "pokemon_heridos": pokemones.filter(current_hp__gt=0, current_hp__lt=models.F('pokemon__hp')).count(),
            "pokemon_derrotados": pokemones.filter(current_hp__lte=0).count(),
            "pokemon_lista": []
        }

        for user_pokemon in pokemones:
            pokemon_info = {
                "user_pokemon_id": user_pokemon.id,
                "nombre": user_pokemon.pokemon.name,
                "hp_actual": user_pokemon.current_hp,
                "hp_maximo": user_pokemon.pokemon.hp,
                "estado": "sano" if user_pokemon.current_hp == user_pokemon.pokemon.hp else
                "herido" if user_pokemon.current_hp > 0 else
                "derrotado"
            }
            estadisticas["pokemon_lista"].append(pokemon_info)

        return Response(estadisticas)