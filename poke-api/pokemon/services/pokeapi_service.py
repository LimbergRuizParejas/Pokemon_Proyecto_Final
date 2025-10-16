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

    def guardar_pokemon_en_bd(self, datos_pokeapi):
        """Transforma los datos de PokeAPI y guarda en nuestra BD"""
        try:
            # Verificar si el pokémon ya existe en nuestra BD
            pokemon, created = Pokemon.objects.get_or_create(
                name=datos_pokeapi['name'],
                defaults={
                    'base_experience': datos_pokeapi['base_experience'],
                    'height': datos_pokeapi['height'],
                    'weight': datos_pokeapi['weight'],
                    'sprite_front': datos_pokeapi['sprites']['front_default'],
                    'sprite_back': datos_pokeapi['sprites']['back_default'],
                    'hp': 0,  # Valores temporales, se actualizarán después
                    'attack': 0,
                    'defense': 0,
                    'special_attack': 0,
                    'special_defense': 0,
                    'speed': 0,
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
            # Filtrar movimientos que tienen detalles disponibles
            movimientos_con_detalles = [m for m in movimientos_data if m['version_group_details']]

            if len(movimientos_con_detalles) >= 4:
                movimientos_seleccionados = random.sample(movimientos_con_detalles, 4)
            else:
                movimientos_seleccionados = movimientos_con_detalles

            movimientos_guardados = 0
            for movimiento_data in movimientos_seleccionados:
                if movimientos_guardados >= 4:
                    break

                movimiento_url = movimiento_data['move']['url']
                detalle_movimiento = self.obtener_detalle_movimiento(movimiento_url)

                if detalle_movimiento:
                    # Solo guardar movimientos que tienen poder (no None) y son de la generación 1
                    if detalle_movimiento.get('power') is not None:
                        # Obtener tipo del movimiento
                        tipo_movimiento_data = detalle_movimiento['type']
                        tipo_movimiento = self.obtener_o_crear_tipo(tipo_movimiento_data)

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
                        movimientos_guardados += 1

            # Si no conseguimos 4 movimientos con poder, agregar algunos sin poder como fallback
            if movimientos_guardados < 4:
                movimientos_fallback = [m for m in movimientos_data if m not in movimientos_seleccionados]
                for movimiento_data in movimientos_fallback[:4 - movimientos_guardados]:
                    movimiento_url = movimiento_data['move']['url']
                    detalle_movimiento = self.obtener_detalle_movimiento(movimiento_url)

                    if detalle_movimiento:
                        tipo_movimiento_data = detalle_movimiento['type']
                        tipo_movimiento = self.obtener_o_crear_tipo(tipo_movimiento_data)

                        movimiento, mov_created = Movimiento.objects.get_or_create(
                            name=movimiento_data['move']['name'],
                            defaults={
                                'power': detalle_movimiento.get('power', 50),  # Valor por defecto
                                'pp': detalle_movimiento.get('pp', 20),
                                'accuracy': detalle_movimiento.get('accuracy', 100),
                                'tipo': tipo_movimiento
                            }
                        )
                        pokemon.movimientos.add(movimiento)
                        movimientos_guardados += 1

            pokemon.save()
            return pokemon

        except Exception as e:
            print(f"Error guardando pokémon: {e}")
            return None

    def obtener_pokemon_por_nombre(self, nombre):
        """Obtiene un pokémon por nombre de la PokeAPI"""
        response = requests.get(f"{self.BASE_URL}/pokemon/{nombre.lower()}")
        if response.status_code == 200:
            return response.json()
        return None

    def obtener_pokemones_iniciales(self):
        """Obtiene los 3 pokémones iniciales: Bulbasaur, Charmander, Squirtle"""
        iniciales = ['bulbasaur', 'charmander', 'squirtle']
        pokemones = []

        for nombre in iniciales:
            pokemon_data = self.obtener_pokemon_por_nombre(nombre)
            if pokemon_data:
                pokemones.append(pokemon_data)

        return pokemones

    def obtener_pokemon_con_movimientos_aleatorios(self, pokemon_data):
        """Obtiene un pokémon con 4 movimientos aleatorios (sin guardar en BD)"""
        # Procesar movimientos (elegir 4 aleatorios)
        movimientos_data = pokemon_data['moves']
        # Filtrar movimientos que tienen detalles disponibles
        movimientos_con_detalles = [m for m in movimientos_data if m['version_group_details']]

        if len(movimientos_con_detalles) >= 4:
            movimientos_seleccionados = random.sample(movimientos_con_detalles, 4)
        else:
            movimientos_seleccionados = movimientos_con_detalles

        movimientos_info = []
        for movimiento_data in movimientos_seleccionados:
            movimiento_url = movimiento_data['move']['url']
            detalle_movimiento = self.obtener_detalle_movimiento(movimiento_url)

            if detalle_movimiento and detalle_movimiento.get('power') is not None:
                movimiento_info = {
                    'name': movimiento_data['move']['name'],
                    'power': detalle_movimiento.get('power'),
                    'pp': detalle_movimiento.get('pp', 20),
                    'accuracy': detalle_movimiento.get('accuracy'),
                    'tipo': detalle_movimiento['type']['name']
                }
                movimientos_info.append(movimiento_info)

        # Si no conseguimos 4 movimientos con poder, agregar algunos sin poder como fallback
        if len(movimientos_info) < 4:
            movimientos_fallback = [m for m in movimientos_data if m not in movimientos_seleccionados]
            for movimiento_data in movimientos_fallback[:4 - len(movimientos_info)]:
                movimiento_url = movimiento_data['move']['url']
                detalle_movimiento = self.obtener_detalle_movimiento(movimiento_url)

                if detalle_movimiento:
                    movimiento_info = {
                        'name': movimiento_data['move']['name'],
                        'power': detalle_movimiento.get('power', 50),  # Valor por defecto
                        'pp': detalle_movimiento.get('pp', 20),
                        'accuracy': detalle_movimiento.get('accuracy', 100),
                        'tipo': detalle_movimiento['type']['name']
                    }
                    movimientos_info.append(movimiento_info)

        return movimientos_info
