from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.pokenmon_viewset import (
    PokemonViewSet,
    UserPokemonViewSet,
    BatallaViewSet,
    PokeAPIViewSet
)

router = DefaultRouter()
router.register(r'pokemons', PokemonViewSet, basename='pokemon')
router.register(r'mis-pokemones', UserPokemonViewSet, basename='user-pokemon')
router.register(r'batallas', BatallaViewSet, basename='batalla')
router.register(r'pokeapi', PokeAPIViewSet, basename='pokeapi')

urlpatterns = [
    path('', include(router.urls)),
]