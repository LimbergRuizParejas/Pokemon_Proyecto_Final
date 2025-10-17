import random
from ..models import Movimiento, Pokemon, UserPokemon, Batalla


class CombatService:

    @staticmethod
    def calcular_multiplicador_efectividad(movimiento, pokemon_defensor):
        tipo_ataque = movimiento.tipo
        multiplicador_total = 1.0

        for tipo_defensor in pokemon_defensor.tipos.all():
            efectividad = tipo_defensor.calcular_multiplicador_danio(tipo_ataque.name)
            multiplicador_total *= efectividad

        return multiplicador_total

    @staticmethod
    def calcular_danio(movimiento, pokemon_atacante, pokemon_defensor):
        if movimiento.power is None:
            return {
                'danio': 0,
                'multiplicador_efectividad': 1.0,
                'efectividad': "Sin daño"
            }

        poder = movimiento.power

        ataque = pokemon_atacante.attack
        defensa = pokemon_defensor.defense

        nivel = 50
        danio_base = (((2 * nivel / 5 + 2) * poder * ataque / defensa) / 50) + 2

        multiplicador_efectividad = CombatService.calcular_multiplicador_efectividad(
            movimiento, pokemon_defensor
        )

        danio_efectivo = danio_base * multiplicador_efectividad

        variacion = random.uniform(0.85, 1.0)
        danio_final = danio_efectivo * variacion

        return {
            'danio': int(max(1, danio_final)),
            'multiplicador_efectividad': multiplicador_efectividad,
            'efectividad': CombatService.obtener_texto_efectividad(multiplicador_efectividad)
        }

    @staticmethod
    def obtener_texto_efectividad(multiplicador):
        if multiplicador == 0.0:
            return "No afecta"
        elif multiplicador <= 0.5:
            return "No es muy efectivo"
        elif multiplicador >= 2.0:
            return "Es super efectivo!"
        elif multiplicador > 1.0:
            return "Es muy efectivo"
        else:
            return "Normal"

    @staticmethod
    def ejecutar_ataque(movimiento_id, user_pokemon, pokemon_salvaje):
        try:
            movimiento = Movimiento.objects.get(id=movimiento_id)

            if movimiento not in user_pokemon.pokemon.movimientos.all():
                return {"error": "El movimiento no pertenece a este pokémon"}

            resultado = CombatService.calcular_danio(
                movimiento,
                user_pokemon.pokemon,
                pokemon_salvaje
            )

            resultado['atacante'] = user_pokemon.pokemon.name
            resultado['defensor'] = pokemon_salvaje.name
            resultado['movimiento'] = movimiento.name

            return resultado

        except Movimiento.DoesNotExist:
            return {"error": "Movimiento no encontrado"}

    @staticmethod
    def determinar_quien_ataca_primero(user_pokemon, pokemon_salvaje):
        velocidad_usuario = user_pokemon.pokemon.speed
        velocidad_salvaje = pokemon_salvaje.speed

        if velocidad_usuario > velocidad_salvaje:
            return 'usuario'
        elif velocidad_salvaje > velocidad_usuario:
            return 'salvaje'
        else:
            return random.choice(['usuario', 'salvaje'])