"""
Configuración de URLs del módulo Pokémon
-----------------------------------------
Incluye:
- /api/pokemon/pokemons/      → CRUD de Pokémon
- /api/pokemon/movimientos/   → CRUD de Movimientos
- /api/pokemon/tipos/         → CRUD de Tipos
- /api/pokemon/random/        → Obtiene un Pokémon aleatorio
- /api/pokemon/capturar/      → Captura un Pokémon (POST)

Autor: Equipo Pokémon Project
Fecha: 2025-10-23
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 🔹 Importación de viewsets y vistas personalizadas
from pokemon.api.movimiento_viewset import MovimientoViewSet
from pokemon.api.tipo_viewset import TipoViewSet
from pokemon.api.pokenmon_viewset import PokemonViewSet
from pokemon.views import capturar_pokemon  # ✅ vista creada en pokemon/views.py

# ⚙️ Router principal (DRF)
router = DefaultRouter()
router.register(r"pokemons", PokemonViewSet, basename="pokemon")
router.register(r"movimientos", MovimientoViewSet, basename="movimiento")
router.register(r"tipos", TipoViewSet, basename="tipo")

# 🧭 Definición de rutas principales
urlpatterns = [
    # CRUDs generados por los viewsets
    path("", include(router.urls)),

    # 🔹 Endpoint para Pokémon aleatorio
    path("random/", PokemonViewSet.as_view({"get": "random_pokemon"}), name="pokemon-random"),

    # 🔹 Endpoint para capturar Pokémon
    path("capturar/", capturar_pokemon, name="pokemon-capturar"),
]

# 💬 Mensaje de consola al cargar el módulo
print("✅ Rutas del módulo Pokémon cargadas: /pokemons/, /movimientos/, /tipos/, /random/, /capturar/")
