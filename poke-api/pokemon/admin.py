from django.contrib import admin
from .models import Tipo, Movimiento, Pokemon, UserPokemon, Batalla

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'power', 'pp', 'accuracy', 'tipo']
    list_filter = ['tipo']
    search_fields = ['name']

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'base_experience', 'hp']
    list_filter = ['tipos']
    search_fields = ['name']

@admin.register(UserPokemon)
class UserPokemonAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'pokemon', 'is_in_team', 'nivel', 'current_hp']
    list_filter = ['is_in_team', 'user']
    search_fields = ['user__username', 'pokemon__name']

@admin.register(Batalla)
class BatallaAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'pokemon_salvaje', 'estado', 'created_at']
    list_filter = ['estado', 'created_at']
    search_fields = ['user__username', 'pokemon_salvaje__name']