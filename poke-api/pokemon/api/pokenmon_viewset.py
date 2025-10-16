from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.shortcuts import get_object_or_404
import requests
import random
from pokemon.models import Pokemon, UserPokemon, Batalla, Tipo, Movimiento


class PokemonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Pokemon.objects.all()

    class PokemonSerializer(serializers.ModelSerializer):
        tipos_nombres = serializers.SerializerMethodField()

        class Meta:
            model = Pokemon
            fields = '__all__'

        def get_tipos_nombres(self, obj):
            return [tipo.name for tipo in obj.tipos.all()]

    serializer_class = PokemonSerializer


class UserPokemonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    class UserPokemonSerializer(serializers.ModelSerializer):
        pokemon_nombre = serializers.CharField(source='pokemon.name', read_only=True)
        pokemon_tipos = serializers.SerializerMethodField()
        pokemon_sprite_front = serializers.URLField(source='pokemon.sprite_front', read_only=True)

        class Meta:
            model = UserPokemon
            fields = '__all__'
            read_only_fields = ('user', 'current_hp', 'experiencia')

        def get_pokemon_tipos(self, obj):
            return [tipo.name for tipo in obj.pokemon.tipos.all()]

    serializer_class = UserPokemonSerializer

    def get_queryset(self):
        return UserPokemon.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BatallaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Batalla.objects.all()

    class BatallaSerializer(serializers.ModelSerializer):
        pokemon_salvaje_nombre = serializers.CharField(source='pokemon_salvaje.name', read_only=True)

        class Meta:
            model = Batalla
            fields = '__all__'
            read_only_fields = ('user', 'created_at')

    serializer_class = BatallaSerializer

    def get_queryset(self):
        return Batalla.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PokeAPIViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def pokemon_aleatorio(self, request):
        # Lógica para obtener pokémon aleatorio de PokeAPI
        return Response({"message": "Endpoint para pokémon aleatorio"})

    @action(detail=False, methods=['post'])
    def capturar(self, request):
        # Lógica para capturar pokémon
        return Response({"message": "Endpoint para capturar pokémon"})