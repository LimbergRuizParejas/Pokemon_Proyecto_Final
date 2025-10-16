from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from pokemon.services.pokeapi_service import PokeAPIService


class PokemonAleatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtiene un pokémon aleatorio de la PokeAPI con información completa"""
        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_aleatorio()

        if pokemon_data:
            # Guardar el pokémon en nuestra BD (esto generará los movimientos)
            pokemon_guardado = service.guardar_pokemon_en_bd(pokemon_data)

            if not pokemon_guardado:
                return Response(
                    {"error": "Error al guardar el pokémon en la base de datos"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Obtener información completa de tipos con relaciones de daño
            tipos_info = service.obtener_info_tipos_completa(pokemon_data['types'])

            # Calcular debilidades y resistencias
            relaciones_dano = service.calcular_debilidades_resistencias(tipos_info)

            # Obtener movimientos del pokémon guardado
            movimientos_info = []
            for movimiento in pokemon_guardado.movimientos.all():
                movimientos_info.append({
                    'id': movimiento.id,
                    'name': movimiento.name,
                    'power': movimiento.power,
                    'pp': movimiento.pp,
                    'accuracy': movimiento.accuracy,
                    'tipo': movimiento.tipo.name
                })

            pokemon_info = {
                'id': pokemon_data['id'],
                'name': pokemon_data['name'],
                'sprites': {
                    'front_default': pokemon_data['sprites']['front_default'],
                    'back_default': pokemon_data['sprites']['back_default']
                },
                'types': [tipo_info['name'] for tipo_info in tipos_info],
                'types_detallados': tipos_info,
                'relaciones_dano': relaciones_dano,
                'stats': {s['stat']['name']: s['base_stat'] for s in pokemon_data['stats']},
                'movimientos': movimientos_info,  # ¡Ahora incluye movimientos!
                'height': pokemon_data['height'],
                'weight': pokemon_data['weight'],
                'base_experience': pokemon_data['base_experience'],
                'pokemon_db_id': pokemon_guardado.id  # ID en nuestra base de datos
            }
            return Response(pokemon_info)

        return Response(
            {"error": "No se pudo obtener pokémon de la PokeAPI"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TestRelacionesDanioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Endpoint para probar relaciones de daño entre tipos"""
        from pokemon.models import Tipo

        # Ejemplo: probar tipo Electrico vs varios tipos
        tipo_electrico = Tipo.objects.get(name='electric')

        tests = [
            ('ground', 'Electrico vs Ground'),
            ('flying', 'Electrico vs Flying'),
            ('water', 'Electrico vs Water'),
            ('electric', 'Electrico vs Electric'),
        ]

        resultados = []
        for tipo_defensa, descripcion in tests:
            multiplicador = tipo_electrico.calcular_multiplicador_danio(tipo_defensa)
            resultados.append({
                'test': descripcion,
                'multiplicador': multiplicador,
                'efectividad': self.obtener_efectividad_texto(multiplicador)
            })

        return Response(resultados)

    def obtener_efectividad_texto(self, multiplicador):
        if multiplicador == 0.0:
            return "No afecta"
        elif multiplicador == 0.5:
            return "No muy efectivo"
        elif multiplicador == 1.0:
            return "Normal"
        elif multiplicador == 2.0:
            return "Super efectivo!"
        else:
            return f"Multiplicador {multiplicador}"
