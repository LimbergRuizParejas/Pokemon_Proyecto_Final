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
        """Obtiene las relaciones de daño de un tipo desde PokeAPI"""
        response = requests.get(tipo_url)
        if response.status_code != 200:
            return {}

        data = response.json()
        damage_relations = data['damage_relations']

        # Extraer solo los nombres de las relaciones
        relaciones_simplificadas = {
            'double_damage_from': [{'name': t['name']} for t in damage_relations['double_damage_from']],
            'double_damage_to': [{'name': t['name']} for t in damage_relations['double_damage_to']],
            'half_damage_from': [{'name': t['name']} for t in damage_relations['half_damage_from']],
            'half_damage_to': [{'name': t['name']} for t in damage_relations['half_damage_to']],
            'no_damage_from': [{'name': t['name']} for t in damage_relations['no_damage_from']],
            'no_damage_to': [{'name': t['name']} for t in damage_relations['no_damage_to']],
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

    def guardar_pokemon_en_bd(self, datos_pokeapi):
        """Transforma los datos de PokeAPI y guarda en nuestra BD"""
        try:
            # Crear o obtener el pokémon
            pokemon, created = Pokemon.objects.get_or_create(
                name=datos_pokeapi['name'],
                defaults={
                    'base_experience': datos_pokeapi['base_experience'],
                    'height': datos_pokeapi['height'],
                    'weight': datos_pokeapi['weight'],
                    'sprite_front': datos_pokeapi['sprites']['front_default'],
                    'sprite_back': datos_pokeapi['sprites']['back_default'],
                }
            )

            # Si el pokémon ya existe, retornarlo (evitar duplicados)
            if not created:
                return pokemon

            # Procesar tipos
            for tipo_data in datos_pokeapi['types']:
                tipo = self.obtener_o_crear_tipo(tipo_data['type'])
                pokemon.tipos.add(tipo)

            # Procesar stats
            stats = {stat['stat']['name']: stat['base_stat'] for stat in datos_pokeapi['stats']}
            pokemon.hp = stats.get('hp', 50)
            pokemon.attack = stats.get('attack', 50)
            pokemon.defense = stats.get('defense', 50)
            pokemon.special_attack = stats.get('special-attack', 50)
            pokemon.special_defense = stats.get('special-defense', 50)
            pokemon.speed = stats.get('speed', 50)

            # Procesar movimientos (elegir 4 aleatorios)
            movimientos_data = datos_pokeapi['moves']
            movimientos_seleccionados = random.sample(
                movimientos_data,
                min(4, len(movimientos_data))
            )

            for movimiento_data in movimientos_seleccionados:
                movimiento_url = movimiento_data['move']['url']
                detalle_movimiento = self.obtener_detalle_movimiento(movimiento_url)

                if detalle_movimiento and detalle_movimiento.get('power') is not None:
                    # Obtener tipo del movimiento
                    tipo_movimiento = self.obtener_o_crear_tipo(detalle_movimiento['type'])

                    # Crear o obtener el movimiento
                    movimiento, mov_created = Movimiento.objects.get_or_create(
                        name=movimiento_data['move']['name'],
                        defaults={
                            'power': detalle_movimiento.get('power'),
                            'pp': detalle_movimiento.get('pp', 20),
                            'accuracy': detalle_movimiento.get('accuracy'),
                            'tipo': tipo_movimiento
                        }
                    )
                    pokemon.movimientos.add(movimiento)

            pokemon.save()
            return pokemon

        except Exception as e:
            print(f"Error guardando pokémon: {e}")
            return None