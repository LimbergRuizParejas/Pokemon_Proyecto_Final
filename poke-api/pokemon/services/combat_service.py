import random
from ..models import Movimiento, Pokemon, UserPokemon


class CombatService:
    @staticmethod
    def calcular_multiplicador_efectividad(movimiento, pokemon_defensor):
        """Calcula el multiplicador de efectividad basado en tipos"""
        tipo_ataque = movimiento.tipo
        multiplicador_total = 1.0

        for tipo_defensor in pokemon_defensor.tipos.all():
            efectividad = tipo_defensor.calcular_multiplicador_danio(tipo_ataque.name)
            multiplicador_total *= efectividad

        return multiplicador_total

    @staticmethod
    def calcular_danio(movimiento, pokemon_atacante, pokemon_defensor):
        """Calcula el daño considerando tipos, stats y relaciones de daño"""
        # Daño base del movimiento
        poder = movimiento.power or 50

        # Stats del atacante y defensor
        ataque = pokemon_atacante.attack
        defensa = pokemon_defensor.defense

        # Cálculo base de daño
        danio_base = (((2 * 50 / 5 + 2) * poder * ataque / defensa) / 50) + 2

        # Multiplicador por efectividad de tipos
        multiplicador_efectividad = CombatService.calcular_multiplicador_efectividad(
            movimiento, pokemon_defensor
        )

        # Daño con efectividad
        danio_efectivo = danio_base * multiplicador_efectividad

        # Variación aleatoria (85% - 100%)
        variacion = random.uniform(0.85, 1.0)
        danio_final = danio_efectivo * variacion

        return {
            'danio': int(max(1, danio_final)),
            'multiplicador_efectividad': multiplicador_efectividad,
            'efectividad': CombatService.obtener_texto_efectividad(multiplicador_efectividad)
        }

    @staticmethod
    def obtener_texto_efectividad(multiplicador):
        """Convierte el multiplicador en texto descriptivo"""
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
        """Ejecuta un ataque en la batalla"""
        try:
            movimiento = Movimiento.objects.get(id=movimiento_id)

            # Verificar que el movimiento pertenece al pokémon del usuario
            if movimiento not in user_pokemon.pokemon.movimientos.all():
                return {"error": "El movimiento no pertenece a este pokémon"}

            # Calcular daño
            resultado = CombatService.calcular_danio(
                movimiento,
                user_pokemon.pokemon,
                pokemon_salvaje
            )

            # Aplicar daño al pokémon salvaje
            resultado['atacante'] = user_pokemon.pokemon.name
            resultado['defensor'] = pokemon_salvaje.name
            resultado['movimiento'] = movimiento.name

            return resultado

        except Movimiento.DoesNotExist:
            return {"error": "Movimiento no encontrado"}