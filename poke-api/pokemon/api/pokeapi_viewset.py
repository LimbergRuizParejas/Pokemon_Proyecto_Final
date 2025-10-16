from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from pokemon.services.pokeapi_service import PokeAPIService


class PokemonAleatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtiene un pokémon aleatorio de la PokeAPI con información completa de tipos"""
        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_aleatorio()

        if pokemon_data:
            # Obtener información completa de tipos con relaciones de daño
            tipos_info = service.obtener_info_tipos_completa(pokemon_data['types'])

            # Calcular debilidades y resistencias
            relaciones_dano = service.calcular_debilidades_resistencias(tipos_info)

            pokemon_info = {
                'id': pokemon_data['id'],
                'name': pokemon_data['name'],
                'sprites': {
                    'front_default': pokemon_data['sprites']['front_default'],
                    'back_default': pokemon_data['sprites']['back_default']
                },
                'types': [tipo_info['name'] for tipo_info in tipos_info],
                'types_detallados': tipos_info,  # Información completa de cada tipo
                'relaciones_dano': relaciones_dano,  # Debilidades, resistencias, inmunidades
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
