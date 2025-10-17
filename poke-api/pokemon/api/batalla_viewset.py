from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.models import Batalla, UserPokemon, Movimiento
from pokemon.services.pokeapi_service import PokeAPIService
from pokemon.services.combat_service import CombatService
from .serializers import PokemonSerializer, UserPokemonSerializer
import random


class BatallaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    class BatallaSerializer(serializers.ModelSerializer):
        pokemon_salvaje = PokemonSerializer(read_only=True)
        user_pokemon_actual = serializers.SerializerMethodField()
        equipo_usuario = serializers.SerializerMethodField()

        class Meta:
            model = Batalla
            fields = '__all__'
            read_only_fields = ('user', 'created_at')

        def get_user_pokemon_actual(self, obj):
            if obj.user_pokemon_actual:
                return UserPokemonSerializer(obj.user_pokemon_actual).data
            return None

        def get_equipo_usuario(self, obj):
            equipo = UserPokemon.objects.filter(user=obj.user, is_in_team=True)
            return UserPokemonSerializer(equipo, many=True).data

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

        user_pokemon_actual = UserPokemon.objects.filter(
            user=self.request.user,
            is_in_team=True,
            current_hp__gt=0
        ).first()

        if not user_pokemon_actual:
            raise serializers.ValidationError("No tienes pokémones vivos en tu equipo")

        serializer.save(
            user=self.request.user,
            pokemon_salvaje=pokemon_salvaje,
            user_pokemon_actual=user_pokemon_actual
        )

    @action(detail=True, methods=['post'])
    def accion(self, request, pk=None):
        batalla = self.get_object()

        if batalla.verificar_fin_batalla():
            return Response(
                {"error": "Esta batalla ha terminado. Todos tus pokémones han sido derrotados."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if batalla.estado != 'activa':
            return Response(
                {"error": "Esta batalla ya ha terminado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        accion = request.data.get('accion')
        user_pokemon_id = request.data.get('user_pokemon_id')
        movimiento_id = request.data.get('movimiento_id')

        try:
            if user_pokemon_id:
                user_pokemon = UserPokemon.objects.get(id=user_pokemon_id, user=request.user)
                if user_pokemon != batalla.user_pokemon_actual:
                    batalla.user_pokemon_actual = user_pokemon
                    batalla.save()
            else:
                user_pokemon = batalla.user_pokemon_actual
        except UserPokemon.DoesNotExist:
            return Response(
                {"error": "Pokémon no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user_pokemon or user_pokemon.current_hp <= 0:
            return Response(
                {"error": "El pokémon actual está debilitado. Cambia de pokémon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if accion == 'atacar':
            return self._manejar_ataque(batalla, user_pokemon, movimiento_id)
        elif accion == 'capturar':
            return self._manejar_captura(batalla, user_pokemon)
        elif accion == 'curar':
            return self._manejar_curacion(batalla, user_pokemon)
        elif accion == 'huir':
            return self._manejar_huida(batalla)
        elif accion == 'cambiar_pokemon':
            return self._manejar_cambio_pokemon(batalla, user_pokemon_id)
        else:
            return Response(
                {"error": "Acción no válida"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _manejar_ataque(self, batalla, user_pokemon, movimiento_id):
        if not movimiento_id:
            return Response(
                {"error": "Se requiere movimiento_id para atacar"},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado_ataque = CombatService.ejecutar_ataque(
            movimiento_id,
            user_pokemon,
            batalla.pokemon_salvaje
        )

        if 'error' in resultado_ataque:
            return Response(resultado_ataque, status=status.HTTP_400_BAD_REQUEST)

        batalla.hp_salvaje_actual -= resultado_ataque['danio']
        if batalla.hp_salvaje_actual < 0:
            batalla.hp_salvaje_actual = 0

        respuesta = {
            "accion": "atacar",
            "resultado_usuario": resultado_ataque,
            "hp_salvaje_restante": batalla.hp_salvaje_actual,
            "hp_usuario_actual": user_pokemon.current_hp
        }

        if batalla.hp_salvaje_actual <= 0:
            batalla.estado = 'ganada'
            batalla.save()
            respuesta.update({
                "mensaje": "¡Has derrotado al pokémon salvaje!",
                "batalla_terminada": True,
                "resultado_batalla": "ganada"
            })
            return Response(respuesta)

        resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, user_pokemon)
        user_pokemon.current_hp -= resultado_contrataque['danio']
        if user_pokemon.current_hp < 0:
            user_pokemon.current_hp = 0

        user_pokemon.save()
        batalla.save()

        respuesta.update({
            "resultado_salvaje": resultado_contrataque,
            "hp_usuario_actual": user_pokemon.current_hp
        })

        if user_pokemon.current_hp <= 0:
            nuevo_pokemon = batalla.obtener_pokemon_actual_usuario()

            if not nuevo_pokemon:
                batalla.estado = 'perdida'
                batalla.save()
                respuesta.update({
                    "mensaje": "¡Todos tus pokémones han sido derrotados!",
                    "batalla_terminada": True,
                    "resultado_batalla": "perdida"
                })
            else:
                respuesta.update({
                    "mensaje": f"¡{user_pokemon.pokemon.name} ha sido derrotado! {nuevo_pokemon.pokemon.name} entra en combate.",
                    "pokemon_derrotado": user_pokemon.id,
                    "nuevo_pokemon_actual": nuevo_pokemon.id,
                    "batalla_terminada": False
                })

        return Response(respuesta)

    def _ejecutar_ataque_salvaje(self, batalla, user_pokemon):
        movimientos_salvaje = list(batalla.pokemon_salvaje.movimientos.all())

        if not movimientos_salvaje:
            return {
                'danio': 10,
                'movimiento': 'Ataque Básico',
                'efectividad': 'Normal'
            }

        movimiento_salvaje = random.choice(movimientos_salvaje)

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
        if batalla.pokebolas_restantes <= 0:
            return Response(
                {"error": "No te quedan pokebolas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hp_porcentaje = (batalla.hp_salvaje_actual / batalla.pokemon_salvaje.hp) * 100
        probabilidad_base = max(10, 100 - hp_porcentaje)

        probabilidad_final = random.uniform(probabilidad_base * 0.5, probabilidad_base)

        batalla.pokebolas_restantes -= 1

        exito_captura = random.random() * 100 <= probabilidad_final

        if exito_captura:
            batalla.estado = 'capturado'
            batalla.save()

            pokemon_existente = UserPokemon.objects.filter(
                user=batalla.user,
                pokemon=batalla.pokemon_salvaje
            ).first()

            if not pokemon_existente:
                nuevo_pokemon = UserPokemon.objects.create(
                    user=batalla.user,
                    pokemon=batalla.pokemon_salvaje,
                    is_in_team=False,
                    current_hp=batalla.pokemon_salvaje.hp,
                    nivel=5
                )

                mensaje = f"¡Felicidades! Has capturado a {batalla.pokemon_salvaje.name}"
                pokemon_info = {
                    "id": nuevo_pokemon.id,
                    "name": batalla.pokemon_salvaje.name,
                    "user_pokemon_id": nuevo_pokemon.id
                }
            else:
                mensaje = f"¡Ya tenías a {batalla.pokemon_salvaje.name}! Se ha liberado."
                pokemon_info = None

            return Response({
                "accion": "capturar",
                "resultado": "éxito",
                "mensaje": mensaje,
                "pokemon_capturado": pokemon_info,
                "batalla_terminada": True,
                "pokebolas_restantes": batalla.pokebolas_restantes
            })
        else:
            batalla.save()

            resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, user_pokemon)

            user_pokemon.current_hp -= resultado_contrataque['danio']
            if user_pokemon.current_hp < 0:
                user_pokemon.current_hp = 0
            user_pokemon.save()

            if user_pokemon.current_hp <= 0:
                nuevo_pokemon = batalla.obtener_pokemon_actual_usuario()
                if not nuevo_pokemon:
                    batalla.estado = 'perdida'
                    batalla.save()
                    return Response({
                        "accion": "capturar",
                        "resultado": "fallo",
                        "mensaje": "¡Todos tus pokémones han sido derrotados!",
                        "batalla_terminada": True,
                        "resultado_batalla": "perdida"
                    })
                else:
                    return Response({
                        "accion": "capturar",
                        "resultado": "fallo",
                        "mensaje": f"¡Oh no! {batalla.pokemon_salvaje.name} ha escapado de la pokebola y {user_pokemon.pokemon.name} ha sido derrotado! {nuevo_pokemon.pokemon.name} entra en combate.",
                        "resultado_salvaje": resultado_contrataque,
                        "hp_actual_usuario": nuevo_pokemon.current_hp,
                        "pokebolas_restantes": batalla.pokebolas_restantes,
                        "batalla_terminada": False,
                        "nuevo_pokemon_actual": nuevo_pokemon.id
                    })

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
        if batalla.curaciones_restantes <= 0:
            return Response(
                {"error": "No te quedan curaciones"},
                status=status.HTTP_400_BAD_REQUEST
            )

        curacion = 50
        hp_maximo = user_pokemon.pokemon.hp
        nuevo_hp = min(user_pokemon.current_hp + curacion, hp_maximo)
        curacion_real = nuevo_hp - user_pokemon.current_hp

        user_pokemon.current_hp = nuevo_hp
        batalla.curaciones_restantes -= 1

        user_pokemon.save()
        batalla.save()

        resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, user_pokemon)

        user_pokemon.current_hp -= resultado_contrataque['danio']
        if user_pokemon.current_hp < 0:
            user_pokemon.current_hp = 0
        user_pokemon.save()

        if user_pokemon.current_hp <= 0:
            nuevo_pokemon = batalla.obtener_pokemon_actual_usuario()
            if not nuevo_pokemon:
                batalla.estado = 'perdida'
                batalla.save()
                return Response({
                    "accion": "curar",
                    "curacion_aplicada": curacion_real,
                    "mensaje": "¡Todos tus pokémones han sido derrotados!",
                    "batalla_terminada": True,
                    "resultado_batalla": "perdida"
                })
            else:
                return Response({
                    "accion": "curar",
                    "curacion_aplicada": curacion_real,
                    "mensaje": f"¡{user_pokemon.pokemon.name} ha sido derrotado después de curar! {nuevo_pokemon.pokemon.name} entra en combate.",
                    "resultado_salvaje": resultado_contrataque,
                    "hp_actual_usuario": nuevo_pokemon.current_hp,
                    "curaciones_restantes": batalla.curaciones_restantes,
                    "batalla_terminada": False,
                    "nuevo_pokemon_actual": nuevo_pokemon.id
                })

        return Response({
            "accion": "curar",
            "curacion_aplicada": curacion_real,
            "hp_actual_usuario": user_pokemon.current_hp,
            "curaciones_restantes": batalla.curaciones_restantes,
            "resultado_salvaje": resultado_contrataque,
            "batalla_terminada": False
        })

    def _manejar_huida(self, batalla):
        batalla.estado = 'escapada'
        batalla.save()

        return Response({
            "accion": "huir",
            "resultado": "éxito",
            "mensaje": "Has escapado de la batalla",
            "batalla_terminada": True
        })

    def _manejar_cambio_pokemon(self, batalla, user_pokemon_id):
        try:
            nuevo_pokemon = UserPokemon.objects.get(id=user_pokemon_id, user=batalla.user)

            if nuevo_pokemon.current_hp <= 0:
                return Response(
                    {"error": "No puedes cambiar a un pokémon debilitado"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            batalla.user_pokemon_actual = nuevo_pokemon
            batalla.save()

            resultado_contrataque = self._ejecutar_ataque_salvaje(batalla, nuevo_pokemon)
            nuevo_pokemon.current_hp -= resultado_contrataque['danio']
            if nuevo_pokemon.current_hp < 0:
                nuevo_pokemon.current_hp = 0
            nuevo_pokemon.save()

            return Response({
                "accion": "cambiar_pokemon",
                "mensaje": f"¡Ve {nuevo_pokemon.pokemon.name}!",
                "nuevo_pokemon_actual": nuevo_pokemon.id,
                "resultado_salvaje": resultado_contrataque,
                "hp_actual_usuario": nuevo_pokemon.current_hp,
                "batalla_terminada": False
            })

        except UserPokemon.DoesNotExist:
            return Response(
                {"error": "Pokémon no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
