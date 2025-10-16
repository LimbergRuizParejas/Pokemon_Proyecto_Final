from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pokemon.api import PokemonViewSet, UserPokemonViewSet, BatallaViewSet, PokeAPIViewSet

router = DefaultRouter()
router.register(r'pokemons', PokemonViewSet, basename='pokemon')
router.register(r'mis-pokemones', UserPokemonViewSet, basename='user-pokemon')
router.register(r'batallas', BatallaViewSet, basename='batalla')


pokeapi_viewset = PokeAPIViewSet.as_view({
    'get': 'pokemon_aleatorio'
})

urlpatterns = [
    path('', include(router.urls)),
    path('pokeapi/pokemon-aleatorio/', pokeapi_viewset, name='pokeapi-pokemon-aleatorio'),
]