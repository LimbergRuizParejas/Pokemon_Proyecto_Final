"""
pokemon_viewset.py
------------------
Controlador principal del módulo Pokémon.

Incluye:
 - CRUD completo (ModelViewSet)
 - Integración con la PokeAPI oficial
 - Endpoint para obtener Pokémon aleatorios
 - Endpoint para capturar Pokémon (simulación con límite de 10)
"""

import random
import requests
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from pokemon.models.pokemon import Pokemon
from pokemon.models.tipo import Tipo


# ============================================================
# 🔹 SERIALIZADORES
# ============================================================
class TipoSerializer(serializers.ModelSerializer):
    """Serializador del modelo Tipo."""
    class Meta:
        model = Tipo
        fields = ["id", "name"]


class PokemonSerializer(serializers.ModelSerializer):
    """Serializador principal del modelo Pokémon."""
    tipo = TipoSerializer(read_only=True)

    class Meta:
        model = Pokemon
        fields = ["id", "name", "hp", "attack", "defense", "image", "tipo"]


# ============================================================
# 🔹 VIEWSET PRINCIPAL
# ============================================================
class PokemonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar Pokémon locales e integrados con la PokeAPI.
    Soporta CRUD completo + obtención de Pokémon aleatorios.
    """

    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer

    # --------------------------------------------------------
    # 🔸 Obtener Pokémon por ID o nombre (local o remoto)
    # --------------------------------------------------------
    def retrieve(self, request, pk=None):
        """Devuelve un Pokémon local o lo importa desde la PokeAPI si no existe."""
        try:
            pokemon = (
                Pokemon.objects.get(pk=pk)
                if pk.isdigit()
                else Pokemon.objects.get(name__iexact=pk)
            )
            return Response(self.get_serializer(pokemon).data)

        except Pokemon.DoesNotExist:
            # Buscar en la PokeAPI si no existe localmente
            url = f"https://pokeapi.co/api/v2/pokemon/{pk.lower()}/"
            try:
                response = requests.get(url, timeout=8)
                response.raise_for_status()
            except requests.RequestException:
                return Response(
                    {"error": "Error al conectar con la PokeAPI."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            data = response.json()
            tipo_name = data["types"][0]["type"]["name"]
            tipo, _ = Tipo.objects.get_or_create(name=tipo_name)

            pokemon = Pokemon.objects.create(
                name=data["name"],
                hp=data["stats"][0]["base_stat"],
                attack=data["stats"][1]["base_stat"],
                defense=data["stats"][2]["base_stat"],
                image=data["sprites"]["front_default"],
                tipo=tipo,
            )

            return Response(
                self.get_serializer(pokemon).data,
                status=status.HTTP_201_CREATED,
            )

    # --------------------------------------------------------
    # 🔸 /api/pokemon/random/
    # --------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="random")
    def random_pokemon(self, request):
        """Devuelve un Pokémon aleatorio local o uno nuevo desde la PokeAPI."""
        pokemons = Pokemon.objects.all()

        if not pokemons.exists():
            random_id = random.randint(1, 151)
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{random_id}/")

            if response.status_code != 200:
                return Response(
                    {"error": "No se pudo obtener un Pokémon aleatorio."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            data = response.json()
            tipo_name = data["types"][0]["type"]["name"]
            tipo, _ = Tipo.objects.get_or_create(name=tipo_name)

            pokemon = Pokemon.objects.create(
                name=data["name"],
                hp=data["stats"][0]["base_stat"],
                attack=data["stats"][1]["base_stat"],
                defense=data["stats"][2]["base_stat"],
                image=data["sprites"]["front_default"],
                tipo=tipo,
            )

            return Response(
                self.get_serializer(pokemon).data,
                status=status.HTTP_201_CREATED,
            )

        pokemon = random.choice(pokemons)
        return Response(self.get_serializer(pokemon).data, status=status.HTTP_200_OK)

    # --------------------------------------------------------
    # 🔸 Crear Pokémon manualmente (sin PokeAPI)
    # --------------------------------------------------------
    def create(self, request, *args, **kwargs):
        """Crea un Pokémon manualmente (desde panel o API)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tipo_data = request.data.get("tipo")
        tipo = None
        if tipo_data:
            tipo, _ = Tipo.objects.get_or_create(name=tipo_data)

        pokemon = serializer.save(tipo=tipo)
        return Response(
            self.get_serializer(pokemon).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# 🔹 ENDPOINT PERSONALIZADO: CAPTURAR POKÉMON
# ============================================================
@api_view(["POST"])
def capturar_pokemon(request):
    """
    Permite 'capturar' un Pokémon existente (simulación con límite de 10).
    
    Ejemplo:
      POST /api/pokemon/capturar/
      { "name": "Pikachu" }
    """
    name = request.data.get("name")
    if not name:
        return Response(
            {"error": "Debes especificar el nombre del Pokémon."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        pokemon = Pokemon.objects.get(name__iexact=name)
    except Pokemon.DoesNotExist:
        return Response(
            {"error": f"El Pokémon '{name}' no existe."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 🔸 Simular límite de 10 capturas
    if Pokemon.objects.count() >= 10:
        return Response(
            {"error": "Has alcanzado el máximo de 10 Pokémon capturados."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PokemonSerializer(pokemon)
    return Response(
        {
            "message": f"🎯 ¡Has capturado a {pokemon.name.title()}!",
            "pokemon": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )
