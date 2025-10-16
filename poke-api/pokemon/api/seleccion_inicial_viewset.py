from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.services.user_service import UserService
from pokemon.services.pokeapi_service import PokeAPIService


class SeleccionInicialViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def opciones(self, request):
        """Obtiene las 3 opciones de pokémones iniciales disponibles con sus movimientos"""
        # Verificar si el usuario ya eligió un pokémon inicial
        if UserService.usuario_tiene_pokemon_inicial(request.user):
            return Response(
                {"error": "Ya has elegido tu pokémon inicial"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pokemones_data = UserService.obtener_opciones_iniciales()
            opciones = []
            for pokemon_data in pokemones_data:
                # Obtener información de tipos
                tipos = [tipo['type']['name'] for tipo in pokemon_data['types']]
                # Obtener stats
                stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data['stats']}

                opcion = {
                    'name': pokemon_data['name'],
                    'sprites': {
                        'front_default': pokemon_data['sprites']['front_default'],
                        'back_default': pokemon_data['sprites']['back_default']
                    },
                    'types': tipos,
                    'stats': stats,
                    'movimientos': pokemon_data['movimientos_aleatorios'],  # Movimientos ya generados
                    'height': pokemon_data['height'],
                    'weight': pokemon_data['weight'],
                    'base_experience': pokemon_data['base_experience']
                }
                opciones.append(opcion)

            return Response(opciones)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def elegir(self, request):
        """Permite al usuario elegir UN pokémon inicial"""
        # Verificar si el usuario ya eligió un pokémon inicial
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
            # Obtener las opciones para encontrar los movimientos del pokémon elegido
            pokemones_data = UserService.obtener_opciones_iniciales()
            movimientos_elegidos = None

            for pokemon_data in pokemones_data:
                if pokemon_data['name'] == nombre_pokemon.lower():
                    movimientos_elegidos = pokemon_data['movimientos_aleatorios']
                    break

            if not movimientos_elegidos:
                return Response(
                    {"error": "No se encontraron movimientos para el pokémon elegido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Elegir el pokémon con sus movimientos específicos
            user_pokemon = UserService.elegir_pokemon_inicial(
                request.user,
                nombre_pokemon,
                movimientos_elegidos
            )

            # Obtener los movimientos del pokémon guardado para incluirlos en la respuesta
            movimientos_info = []
            for movimiento in user_pokemon.pokemon.movimientos.all():
                movimientos_info.append({
                    'id': movimiento.id,
                    'name': movimiento.name,
                    'power': movimiento.power,
                    'pp': movimiento.pp,
                    'accuracy': movimiento.accuracy,
                    'tipo': movimiento.tipo.name
                })

            return Response({
                "message": f"¡Felicidades! Has elegido a {user_pokemon.pokemon.name} como tu pokémon inicial.",
                "pokemon_id": user_pokemon.id,
                "pokemon_nombre": user_pokemon.pokemon.name,
                "movimientos": movimientos_info
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )