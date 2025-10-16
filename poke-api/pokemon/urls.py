from django.urls import path, include
from rest_framework.routers import DefaultRouter

from pokemon.api import PokemonViewSet, UserPokemonViewSet, BatallaViewSet, PokemonAleatorioView, \
    TestRelacionesDanioView, SeleccionInicialViewSet

router = DefaultRouter()
router.register(r'pokemons', PokemonViewSet, basename='pokemon')
router.register(r'mis-pokemones', UserPokemonViewSet, basename='user-pokemon')
router.register(r'batallas', BatallaViewSet, basename='batalla')
router.register(r'seleccion-inicial', SeleccionInicialViewSet, basename='seleccion-inicial')

urlpatterns = [
    path('', include(router.urls)),
    # Ruta simple para pokémon aleatorio - SIN el diccionario
    path('pokeapi/pokemon-aleatorio/', PokemonAleatorioView.as_view(), name='pokeapi-pokemon-aleatorio'),
    path('test/relaciones-danio/', TestRelacionesDanioView.as_view(), name='test-relaciones-danio'),
]
