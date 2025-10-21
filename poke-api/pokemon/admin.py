from django.contrib import admin
from .models import Tipo, Movimiento

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'power', 'pp', 'accuracy', 'tipo']
    list_filter = ['tipo']
    search_fields = ['name']
