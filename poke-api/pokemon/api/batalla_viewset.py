from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.models import Batalla, UserPokemon, Movimiento
from pokemon.services.pokeapi_service import PokeAPIService
from pokemon.services.combat_service import CombatService
import random


class BatallaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    class BatallaSerializer(serializers.ModelSerializer):
        pokemon_salvaje_nombre = serializers.CharField(source='pokemon_salvaje.name', read_only=True)
        pokemon_salvaje_sprite = serializers.URLField(source='pokemon_salvaje.sprite_front', read_only=True)
        pokemon_salvaje_tipos = serializers.SerializerMethodField()
        pokemon_salvaje_hp_actual = serializers.SerializerMethodField()
        pokemon_salvaje_hp_max = serializers.IntegerField(source='pokemon_salvaje.hp', read_only=True)
        pokemon_salvaje_movimientos = serializers.SerializerMethodField()

        class Meta:
            model = Batalla
            fields = '__all__'
            read_only_fields = ('user', 'created_at')

        def get_pokemon_salvaje_tipos(self, obj):
            return [tipo.name for tipo in obj.pokemon_salvaje.tipos.all()]

        def get_pokemon_salvaje_hp_actual(self, obj):
            # En una implementación real, guardaríamos el HP actual del salvaje
            return obj.pokemon_salvaje.hp

        def get_pokemon_salvaje_movimientos(self, obj):
            movimientos = []
            for movimiento in obj.pokemon_salvaje.movimientos.all():
                movimientos.append({
                    'id': movimiento.id,
                    'name': movimiento.name,
                    'power': movimiento.power,
                    'pp': movimiento.pp,
                    'accuracy': movimiento.accuracy,
                    'tipo': movimiento.tipo.name
                })
            return movimientos

    serializer_class = BatallaSerializer

    def get_queryset(self):
        return Batalla.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        service = PokeAPIService()
        pokemon_data = service.obtener_pokemon_aleatorio()

        if not pokemon_data:
            raise serializers.ValidationError("No se pudo obtener pokémon de la PokeAPI")

        pokemon_salvaje = service.guardar_pokemon_en_bd(pokemon_data)

        if not pokemon_salvaje:
            raise serializers.ValidationError("Error al guardar el pokémon salvaje")

        serializer.save(user=self.request.user, pokemon_salvaje=pokemon_salvaje)

    @action(detail=True, methods=['post'])
    def accion(self, request, pk=None):
        """Realiza una acción en la batalla"""
        batalla = self.get_object()

        if batalla.estado != 'activa':
            return Response(
                {"error": "Esta batalla ya ha terminado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        accion = request.data.get('accion')
        user_pokemon_id = request.data.get('user_pokemon_id')
        movimiento_id = request.data.get('movimiento_id')

        try:
            user_pokemon = UserPokemon.objects.get(id=user_pokemon_id, user=request.user)
        except UserPokemon.DoesNotExist:
            return Response(
                {"error": "Pokémon no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        if accion == 'atacar':
            return self._manejar_ataque(batalla, user_pokemon, movimiento_id)
        elif accion == 'capturar':
            return self._manejar_captura(batalla, user_pokemon)
        elif accion == 'curar':
            return self._manejar_curacion(batalla, user_pokemon)
        elif accion == 'huir':
            return self._manejar_huida(batalla)
        else:
            return Response(
                {"error": "Acción no válida"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _manejar_ataque(self, batalla, user_pokemon, movimiento_id):
        """Maneja la acción de ataque"""
        if not movimiento_id:
            return Response(
                {"error": "Se requiere movimiento_id para atacar"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ejecutar ataque del usuario
        resultado_ataque = CombatService.ejecutar_ataque(
            movimiento_id,
            user_pokemon,
            batalla.pokemon_salvaje
        )

        if 'error' in resultado_ataque:
            return Response(resultado_ataque, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el pokémon salvaje fue derrotado
        if resultado_ataque['danio'] >= batalla.pokemon_salvaje.hp:
            batalla.estado = 'ganada'
            batalla.save()
            return Response({
                "accion": "atacar",
                "resultado": resultado_ataque,
                "mensaje": "¡Has derrotado al pokémon salvaje!",
                "batalla_terminada": True,
                "resultado_batalla": "ganada"
            })

        # Turno del pokémon salvaje (ataque aleatorio)
        resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, user_pokemon)

        # Verificar si el pokémon del usuario fue derrotado
        if resultado_contrataque['danio'] >= user_pokemon.current_hp:
            user_pokemon.current_hp = 0
            user_pokemon.save()

            # Verificar si el usuario tiene más pokémones en el equipo
            equipo_vivo = UserPokemon.objects.filter(
                user=batalla.user,
                is_in_team=True,
                current_hp__gt=0
            ).exclude(id=user_pokemon.id)

            if not equipo_vivo.exists():
                batalla.estado = 'perdida'
                batalla.save()
                return Response({
                    "accion": "atacar",
                    "resultado_usuario": resultado_ataque,
                    "resultado_salvaje": resultado_contrataque,
                    "mensaje": "¡Todos tus pokémones han sido derrotados!",
                    "batalla_terminada": True,
                    "resultado_batalla": "perdida"
                })
            else:
                return Response({
                    "accion": "atacar",
                    "resultado_usuario": resultado_ataque,
                    "resultado_salvaje": resultado_contrataque,
                    "mensaje": f"¡{user_pokemon.pokemon.name} ha sido derrotado! Elige otro pokémon.",
                    "pokemon_derrotado": user_pokemon.id,
                    "batalla_terminada": False
                })

        # Actualizar HP del usuario
        user_pokemon.current_hp -= resultado_contrataque['danio']
        user_pokemon.save()

        return Response({
            "accion": "atacar",
            "resultado_usuario": resultado_ataque,
            "resultado_salvaje": resultado_contrataque,
            "hp_actual_usuario": user_pokemon.current_hp,
            "hp_actual_salvaje": batalla.pokemon_salvaje.hp - resultado_ataque['danio'],
            "batalla_terminada": False
        })

    def _ejecutar_ataque_salvaje(self, batalla, user_pokemon):
        """Ejecuta un ataque aleatorio del pokémon salvaje"""
        movimientos_salvaje = list(batalla.pokemon_salvaje.movimientos.all())

        if not movimientos_salvaje:
            # Si no tiene movimientos, usar un ataque básico
            return {
                'danio': 10,
                'movimiento': 'Ataque Básico',
                'efectividad': 'Normal'
            }

        movimiento_salvaje = random.choice(movimientos_salvaje)

        # Usar el servicio de combate para calcular daño
        resultado = CombatService.calcular_danio(
            movimiento_salvaje,
            batalla.pokemon_salvaje,
            user_pokemon.pokemon
        )

        resultado['movimiento'] = movimiento_salvaje.name
        resultado['atacante'] = batalla.pokemon_salvaje.name
        resultado['defensor'] = user_pokemon.pokemon.name

        return resultado

    def _manejar_captura(self, batalla, user_pokemon):
        """Maneja la acción de captura"""
        if batalla.pokebolas_restantes <= 0:
            return Response(
                {"error": "No te quedan pokebolas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calcular probabilidad de captura basada en HP actual
        hp_porcentaje = (batalla.pokemon_salvaje.hp / batalla.pokemon_salvaje.hp) * 100
        probabilidad_base = max(10, 100 - hp_porcentaje)  # Mientras menos HP, más probabilidad

        # Añadir algo de aleatoriedad
        probabilidad_final = random.uniform(probabilidad_base * 0.5, probabilidad_base)

        batalla.pokebolas_restantes -= 1

        if random.random() * 100 <= probabilidad_final:
            # ¡Captura exitosa!
            batalla.estado = 'capturado'
            batalla.save()

            # Crear UserPokemon para el usuario
            nuevo_pokemon = UserPokemon.objects.create(
                user=batalla.user,
                pokemon=batalla.pokemon_salvaje,
                is_in_team=False,  # Va a la reserva inicialmente
                current_hp=batalla.pokemon_salvaje.hp,
                nivel=5
            )

            return Response({
                "accion": "capturar",
                "resultado": "éxito",
                "mensaje": f"¡Felicidades! Has capturado a {batalla.pokemon_salvaje.name}",
                "pokemon_capturado": {
                    "id": nuevo_pokemon.id,
                    "name": batalla.pokemon_salvaje.name,
                    "sprite": batalla.pokemon_salvaje.sprite_front
                },
                "batalla_terminada": True,
                "pokebolas_restantes": batalla.pokebolas_restantes
            })
        else:
            batalla.save()
            # Turno del pokémon salvaje después de fallar captura
            resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, user_pokemon)

            # Actualizar HP del usuario
            user_pokemon.current_hp -= resultado_contrataque['danio']
            user_pokemon.save()

            return Response({
                "accion": "capturar",
                "resultado": "fallo",
                "mensaje": f"¡Oh no! {batalla.pokemon_salvaje.name} ha escapado de la pokebola",
                "resultado_salvaje": resultado_contrataque,
                "hp_actual_usuario": user_pokemon.current_hp,
                "pokebolas_restantes": batalla.pokebolas_restantes,
                "batalla_terminada": False
            })

    def _manejar_curacion(self, batalla, user_pokemon):
        """Maneja la acción de curación"""
        if batalla.curaciones_restantes <= 0:
            return Response(
                {"error": "No te quedan curaciones"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Curar 50 HP o hasta el máximo
        curacion = 50
        hp_maximo = user_pokemon.pokemon.hp
        nuevo_hp = min(user_pokemon.current_hp + curacion, hp_maximo)
        curacion_real = nuevo_hp - user_pokemon.current_hp

        user_pokemon.current_hp = nuevo_hp
        batalla.curaciones_restantes -= 1

        user_pokemon.save()
        batalla.save()

        # Turno del pokémon salvaje después de curar
        resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, user_pokemon)

        # Actualizar HP del usuario después del contrataque
        user_pokemon.current_hp -= resultado_contrataque['danio']
        user_pokemon.save()

        return Response({
            "accion": "curar",
            "curacion_aplicada": curacion_real,
            "hp_actual_usuario": user_pokemon.current_hp,
            "curaciones_restantes": batalla.curaciones_restantes,
            "resultado_salvaje": resultado_contrataque,
            "batalla_terminada": False
        })

    def _manejar_huida(self, batalla):
        """Maneja la acción de huir"""
        batalla.estado = 'escapada'
        batalla.save()

        return Response({
            "accion": "huir",
            "resultado": "éxito",
            "mensaje": "Has escapado de la batalla",
            "batalla_terminada": True
        })
