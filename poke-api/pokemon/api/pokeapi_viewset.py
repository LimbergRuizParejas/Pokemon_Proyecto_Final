from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from pokemon.services.pokeapi_service import PokeAPIService
from .serializers import PokemonSerializer


class PokemonAleatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtiene un pokémon aleatorio de la PokeAPI con estructura estándar"""
        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_aleatorio()

        if pokemon_data:
            # Guardar el pokémon en nuestra BD
            pokemon_guardado = service.guardar_pokemon_en_bd(pokemon_data)

            if not pokemon_guardado:
                return Response(
                    {"error": "Error al guardar el pokémon en la base de datos"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Usar el serializer estándar
            serializer = PokemonSerializer(pokemon_guardado)
            return Response(serializer.data)

        return Response(
            {"error": "No se pudo obtener pokémon de la PokeAPI"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )