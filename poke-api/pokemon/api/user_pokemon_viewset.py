from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pokemon.models import UserPokemon
from .serializers import UserPokemonSerializer


class UserPokemonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPokemonSerializer

    def get_queryset(self):
        return UserPokemon.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        equipo = queryset.filter(is_in_team=True)
        reserva = queryset.filter(is_in_team=False)

        # Verificar límites
        if equipo.count() > 6:
            equipo = equipo[:6]

        if reserva.count() > 10:
            reserva = reserva[:10]

        equipo_serializer = self.get_serializer(equipo, many=True)
        reserva_serializer = self.get_serializer(reserva, many=True)

        return Response({
            'equipo': equipo_serializer.data,
            'reserva': reserva_serializer.data,
            'limites': {
                'max_equipo': 6,
                'max_reserva': 10,
                'actual_equipo': equipo.count(),
                'actual_reserva': reserva.count()
            }
        })

    @action(detail=False, methods=['get'])
    def equipo(self, request):
        equipo = self.get_queryset().filter(is_in_team=True)
        serializer = self.get_serializer(equipo, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reserva(self, request):
        reserva = self.get_queryset().filter(is_in_team=False)
        serializer = self.get_serializer(reserva, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_equipo(self, request, pk=None):
        user_pokemon = self.get_object()

        if user_pokemon.is_in_team:
            reserva_count = self.get_queryset().filter(is_in_team=False).count()
            if reserva_count >= 10:
                return Response(
                    {"error": "Tu reserva está llena (máximo 10 pokémones). Libera uno primero."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_pokemon.is_in_team = False
            user_pokemon.save()

            return Response({
                "message": f"{user_pokemon.pokemon.name} movido a la reserva",
                "nuevo_estado": "reserva"
            })
        else:
            # Mover de reserva a equipo
            equipo_count = self.get_queryset().filter(is_in_team=True).count()
            if equipo_count >= 6:
                return Response(
                    {"error": "Tu equipo está lleno (máximo 6 pokémones). Usa el intercambio para reemplazar uno."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_pokemon.is_in_team = True
            user_pokemon.save()

            return Response({
                "message": f"{user_pokemon.pokemon.name} movido al equipo de combate",
                "nuevo_estado": "equipo"
            })

    @action(detail=True, methods=['post'])
    def liberar(self, request, pk=None):
        user_pokemon = self.get_object()
        nombre_pokemon = user_pokemon.pokemon.name

        user_pokemon.delete()

        return Response({
            "message": f"Has liberado a {nombre_pokemon}",
            "pokemon_liberado": nombre_pokemon
        })

    @action(detail=False, methods=['post'])
    def intercambiar(self, request):
        pokemon_equipo_id = request.data.get('pokemon_equipo_id')
        pokemon_reserva_id = request.data.get('pokemon_reserva_id')

        if not pokemon_equipo_id or not pokemon_reserva_id:
            return Response(
                {"error": "Se requieren ambos IDs: pokemon_equipo_id y pokemon_reserva_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pokemon_equipo = UserPokemon.objects.get(
                id=pokemon_equipo_id,
                user=request.user,
                is_in_team=True
            )

            pokemon_reserva = UserPokemon.objects.get(
                id=pokemon_reserva_id,
                user=request.user,
                is_in_team=False
            )

            pokemon_equipo.is_in_team = False
            pokemon_reserva.is_in_team = True

            pokemon_equipo.save()
            pokemon_reserva.save()

            return Response({
                "message": f"Intercambio exitoso: {pokemon_equipo.pokemon.name} → Reserva, {pokemon_reserva.pokemon.name} → Equipo",
                "intercambio": {
                    "salio_del_equipo": {
                        "user_pokemon_id": pokemon_equipo.id,
                        "nombre": pokemon_equipo.pokemon.name
                    },
                    "entro_al_equipo": {
                        "user_pokemon_id": pokemon_reserva.id,
                        "nombre": pokemon_reserva.pokemon.name
                    }
                }
            })

        except UserPokemon.DoesNotExist:
            return Response(
                {"error": "Uno de los pokémones no fue encontrado o no está en la ubicación esperada"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def reemplazar_en_equipo(self, request):
        pokemon_sale_id = request.data.get('pokemon_sale_id')  # Pokémon que sale del equipo
        pokemon_entra_id = request.data.get('pokemon_entra_id')  # Pokémon que entra al equipo

        if not pokemon_sale_id or not pokemon_entra_id:
            return Response(
                {"error": "Se requieren ambos IDs: pokemon_sale_id y pokemon_entra_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pokemon_sale = UserPokemon.objects.get(
                id=pokemon_sale_id,
                user=request.user,
                is_in_team=True
            )

            pokemon_entra = UserPokemon.objects.get(
                id=pokemon_entra_id,
                user=request.user,
                is_in_team=False
            )

            pokemon_sale.is_in_team = False
            pokemon_entra.is_in_team = True

            pokemon_sale.save()
            pokemon_entra.save()

            return Response({
                "message": f"Reemplazo exitoso: {pokemon_sale.pokemon.name} sale del equipo, {pokemon_entra.pokemon.name} entra al equipo",
                "reemplazo": {
                    "sale_del_equipo": {
                        "user_pokemon_id": pokemon_sale.id,
                        "nombre": pokemon_sale.pokemon.name
                    },
                    "entra_al_equipo": {
                        "user_pokemon_id": pokemon_entra.id,
                        "nombre": pokemon_entra.pokemon.name
                    }
                }
            })

        except UserPokemon.DoesNotExist:
            return Response(
                {"error": "Uno de los pokémones no fue encontrado o no está en la ubicación esperada"},
                status=status.HTTP_404_NOT_FOUND
            )
