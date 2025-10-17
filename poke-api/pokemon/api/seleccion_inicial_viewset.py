from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.services.user_service import UserService
from pokemon.services.pokeapi_service import PokeAPIService
from .serializers import PokemonSerializer


class SeleccionInicialViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def opciones(self, request):
        """Obtiene las 3 opciones de pokémones iniciales con estructura detallada"""
        if UserService.usuario_tiene_pokemon_inicial(request.user):
            return Response(
                {"error": "Ya has elegido tu pokémon inicial"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pokemones_data = UserService.obtener_opciones_iniciales()
            opciones = []

            for pokemon_data in pokemones_data:
                # Guardar el pokémon en BD para obtener estructura completa
                service = PokeAPIService()
                pokemon_guardado = service.guardar_pokemon_en_bd(pokemon_data)

                if pokemon_guardado:
                    # Usar el serializer estándar
                    serializer = PokemonSerializer(pokemon_guardado)
                    opciones.append(serializer.data)

            return Response(opciones)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def elegir(self, request):
        """Permite al usuario elegir UN pokémon inicial"""
        if UserService.usuario_tiene_pokemon_inicial(request.user):
            return Response(
                {"error": "Ya has elegido tu pokémon inicial"},
                status=status.HTTP_400_BAD_REQUEST
            )

        nombre_pokemon = request.data.get('nombre_pokemon')

        if not nombre_pokemon:
            return Response(
                {"error": "Se requiere el nombre del pokémon (bulbasaur, charmander o squirtle)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_pokemon = UserService.elegir_pokemon_inicial(request.user, nombre_pokemon)

            # Usar el serializer de UserPokemon para respuesta consistente
            from .serializers import UserPokemonSerializer
            serializer = UserPokemonSerializer(user_pokemon)

            return Response({
                "message": f"¡Felicidades! Has elegido a {user_pokemon.pokemon.name} como tu pokémon inicial.",
                "pokemon": serializer.data
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )