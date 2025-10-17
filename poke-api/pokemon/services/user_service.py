from authentication.models import User
from pokemon.models import UserPokemon, Movimiento, Tipo
from .pokeapi_service import PokeAPIService
import random


class UserService:
    @staticmethod
    def obtener_opciones_iniciales():
        service = PokeAPIService()
        pokemones_data = service.obtener_pokemones_iniciales()

        for pokemon_data in pokemones_data:
            pokemon_data['movimientos_aleatorios'] = service.obtener_pokemon_con_movimientos_aleatorios(pokemon_data)

        return pokemones_data

    @staticmethod
    def elegir_pokemon_inicial(usuario, nombre_pokemon, movimientos_elegidos=None):
        nombres_permitidos = ['bulbasaur', 'charmander', 'squirtle']
        if nombre_pokemon.lower() not in nombres_permitidos:
            raise Exception("Solo puedes elegir entre Bulbasaur, Charmander o Squirtle")

        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_por_nombre(nombre_pokemon)

        if not pokemon_data:
            raise Exception("No se pudo obtener el pokémon inicial")

        pokemon_guardado = service.guardar_pokemon_en_bd(pokemon_data)

        if not pokemon_guardado:
            raise Exception("Error al guardar el pokémon inicial")

        if movimientos_elegidos:
            UserService._actualizar_movimientos_pokemon(pokemon_guardado, movimientos_elegidos)

        user_pokemon = UserPokemon.objects.create(
            user=usuario,
            pokemon=pokemon_guardado,
            is_in_team=True,
            current_hp=pokemon_guardado.hp,
            nivel=5
        )

        return user_pokemon

    @staticmethod
    def _actualizar_movimientos_pokemon(pokemon, movimientos_data):
        pokemon.movimientos.clear()

        for movimiento_data in movimientos_data:
            tipo_movimiento, _ = Tipo.objects.get_or_create(name=movimiento_data['tipo'])

            movimiento, created = Movimiento.objects.get_or_create(
                name=movimiento_data['name'],
                defaults={
                    'power': movimiento_data.get('power', 50),
                    'pp': movimiento_data.get('pp', 20),
                    'accuracy': movimiento_data.get('accuracy', 100),
                    'tipo': tipo_movimiento
                }
            )
            pokemon.movimientos.add(movimiento)

        pokemon.save()

    @staticmethod
    def usuario_tiene_pokemon_inicial(usuario):
        return UserPokemon.objects.filter(user=usuario).exists()