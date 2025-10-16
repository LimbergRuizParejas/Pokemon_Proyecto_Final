import requests
import random
from ..models import Pokemon, Tipo, Movimiento


class PokeAPIService:
    BASE_URL = "https://pokeapi.co/api/v2"

    def obtener_o_crear_tipo(self, tipo_data):
        """Obtiene o crea un tipo con sus relaciones de daño"""
        tipo_nombre = tipo_data['name']
        tipo, created = Tipo.objects.get_or_create(name=tipo_nombre)

        # Si el tipo es nuevo o no tiene relaciones de daño, obtenerlas
        if created or not tipo.damage_relations:
            tipo.damage_relations = self.obtener_relaciones_dano(tipo_data['url'])
            tipo.save()

        return tipo

    def obtener_relaciones_dano(self, tipo_url):
        response = requests.get(tipo_url)
        if response.status_code != 200:
            return {}

        data = response.json()
        damage_relations = data['damage_relations']
        relaciones_simplificadas = {
            'double_damage_from': [t['name'] for t in damage_relations['double_damage_from']],
            'double_damage_to': [t['name'] for t in damage_relations['double_damage_to']],
            'half_damage_from': [t['name'] for t in damage_relations['half_damage_from']],
            'half_damage_to': [t['name'] for t in damage_relations['half_damage_to']],
            'no_damage_from': [t['name'] for t in damage_relations['no_damage_from']],
            'no_damage_to': [t['name'] for t in damage_relations['no_damage_to']],
        }

        return relaciones_simplificadas

    def obtener_pokemon_aleatorio(self):
        """Obtiene un pokémon aleatorio de la PokeAPI"""
        pokemon_id = random.randint(1, 151)  # Primera generación
        return self.obtener_pokemon_por_id(pokemon_id)

    def obtener_pokemon_por_id(self, pokemon_id):
        """Obtiene un pokémon específico de la PokeAPI"""
        response = requests.get(f"{self.BASE_URL}/pokemon/{pokemon_id}")
        if response.status_code == 200:
            return response.json()
        return None

    def obtener_detalle_movimiento(self, url_movimiento):
        """Obtiene los detalles de un movimiento"""
        response = requests.get(url_movimiento)
        if response.status_code == 200:
            return response.json()
        return None

    def obtener_info_tipos_completa(self, tipos_data):
        """Obtiene información completa de los tipos incluyendo relaciones de daño"""
        tipos_info = []

        for tipo_data in tipos_data:
            tipo = self.obtener_o_crear_tipo(tipo_data['type'])

            tipo_info = {
                'name': tipo.name,
                'damage_relations': tipo.damage_relations
            }
            tipos_info.append(tipo_info)

        return tipos_info

    def calcular_debilidades_resistencias(self, tipos_info):
        """Calcula debilidades y resistencias basado en todos los tipos del pokémon"""
        todas_debilidades = set()
        todas_resistencias = set()
        todas_inmunidades = set()

        for tipo_info in tipos_info:
            damage_relations = tipo_info['damage_relations']

            # Debilidades (doble daño)
            for debilidad in damage_relations.get('double_damage_from', []):
                todas_debilidades.add(debilidad)

            # Resistencias (medio daño)
            for resistencia in damage_relations.get('half_damage_from', []):
                todas_resistencias.add(resistencia)

            # Inmunidades (sin daño)
            for inmunidad in damage_relations.get('no_damage_from', []):
                todas_inmunidades.add(inmunidad)

        # Aplicar lógica de multiplicadores combinados
        debilidades_finales = []
        resistencias_finales = []
        inmunidades_finales = list(todas_inmunidades)

        # Para debilidades: si no está en resistencias o inmunidades
        for debilidad in todas_debilidades:
            if debilidad not in todas_resistencias and debilidad not in todas_inmunidades:
                debilidades_finales.append(debilidad)

        # Para resistencias: si no está en debilidades
        for resistencia in todas_resistencias:
            if resistencia not in todas_debilidades:
                resistencias_finales.append(resistencia)

        return {
            'debilidades': debilidades_finales,
            'resistencias': resistencias_finales,
            'inmunidades': inmunidades_finales
        }