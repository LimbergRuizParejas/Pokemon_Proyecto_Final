from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.services.pokeapi_service import PokeAPIService


class PokeAPIViewSet(viewsets.ViewSet):
    """
    ViewSet para interactuar con la PokeAPI externa
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='pokemon-aleatorio')
    def pokemon_aleatorio(self, request):
        """Obtiene un pokémon aleatorio de la PokeAPI"""
        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_aleatorio()

        if pokemon_data:
            pokemon_info = {
                'id': pokemon_data['id'],
                'name': pokemon_data['name'],
                'sprites': {
                    'front_default': pokemon_data['sprites']['front_default'],
                    'back_default': pokemon_data['sprites']['back_default']
                },
                'types': [t['type']['name'] for t in pokemon_data['types']],
                'stats': {s['stat']['name']: s['base_stat'] for s in pokemon_data['stats']},
                'height': pokemon_data['height'],
                'weight': pokemon_data['weight'],
                'base_experience': pokemon_data['base_experience']
            }
            return Response(pokemon_info)

        return Response(
            {"error": "No se pudo obtener pokémon de la PokeAPI"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )