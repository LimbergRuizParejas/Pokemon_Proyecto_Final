from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pokemon.api import PokemonViewSet, UserPokemonViewSet, BatallaViewSet, PokemonAleatorioView
from pokemon.api.seleccion_inicial_viewset import SeleccionInicialViewSet
from pokemon.api.healing_viewset import HealingViewSet

router = DefaultRouter()
router.register(r'pokemons', PokemonViewSet, basename='pokemon')
router.register(r'mis-pokemones', UserPokemonViewSet, basename='user-pokemon')
router.register(r'batallas', BatallaViewSet, basename='batalla')
router.register(r'seleccion-inicial', SeleccionInicialViewSet, basename='seleccion-inicial')
router.register(r'centro-pokemon', HealingViewSet, basename='healing')  # Nuevo

urlpatterns = [
    path('', include(router.urls)),
    path('pokeapi/pokemon-aleatorio/', PokemonAleatorioView.as_view(), name='pokeapi-pokemon-aleatorio'),
]