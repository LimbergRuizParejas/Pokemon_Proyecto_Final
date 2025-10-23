"""
Vistas del módulo Pokémon
--------------------------
Incluye:
- PokemonViewSet: CRUD completo + endpoint /random/
- TipoViewSet: CRUD de Tipos
- MovimientoViewSet: CRUD de Movimientos
- capturar_pokemon: endpoint personalizado para capturar Pokémon

Autor: Equipo Pokémon Project
Fecha: 2025-10-23
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Pokemon, Tipo, Movimiento
from .serializers import PokemonSerializer, TipoSerializer, MovimientoSerializer
import random

# 🧩 ViewSet principal de Pokémon
class PokemonViewSet(viewsets.ModelViewSet):
    """
    CRUD para Pokémon.
    Incluye un endpoint adicional /random/ para obtener un Pokémon aleatorio.
    """
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer

    @action(detail=False, methods=["get"], url_path="random")
    @method_decorator(cache_page(10))  # cachea la respuesta 10 segundos (optimización)
    def random_pokemon(self, request):
        """
        Devuelve un Pokémon aleatorio del catálogo.
        Si no hay registros, responde con error 404.
        """
        total = self.queryset.count()
        if total == 0:
            return Response(
                {"error": "No hay Pokémon registrados."},
                status=status.HTTP_404_NOT_FOUND,
            )

        pokemon = self.queryset[random.randint(0, total - 1)]
        serializer = self.get_serializer(pokemon)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🌿 ViewSet para Tipos
class TipoViewSet(viewsets.ModelViewSet):
    """
    CRUD para los tipos de Pokémon.
    Ejemplo: fuego, agua, planta, eléctrico...
    """
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer


# ⚡ ViewSet para Movimientos
class MovimientoViewSet(viewsets.ModelViewSet):
    """
    CRUD para los movimientos disponibles en la Pokédex.
    Ejemplo: impacto trueno, lanzallamas, placaje...
    """
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer


# 🎯 Endpoint personalizado: Capturar Pokémon
@api_view(["POST"])
def capturar_pokemon(request):
    """
    Captura un Pokémon por nombre.
    Simula un límite máximo de 10 capturas totales.

    Request:
    {
        "name": "Pikachu"
    }

    Response (201 Created):
    {
        "message": "🎯 ¡Has capturado a Pikachu!",
        "pokemon": { ...datos del Pokémon... }
    }
    """
    nombre = request.data.get("name")

    # ⚠️ Validación básica
    if not nombre:
        return Response(
            {"error": "Falta el nombre del Pokémon."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 🔎 Buscar Pokémon
    try:
        pokemon = Pokemon.objects.get(name__iexact=nombre.strip())
    except Pokemon.DoesNotExist:
        return Response(
            {"error": f"Pokémon '{nombre}' no encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 🚫 Simulación de límite máximo de 10 capturas
    total_capturados = Pokemon.objects.count()
    if total_capturados >= 10:
        return Response(
            {"error": "Ya tienes el máximo de 10 Pokémon capturados."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # ✅ Captura exitosa
    serializer = PokemonSerializer(pokemon)
    return Response(
        {
            "message": f"🎯 ¡Has capturado a {pokemon.name.title()}!",
            "pokemon": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )
