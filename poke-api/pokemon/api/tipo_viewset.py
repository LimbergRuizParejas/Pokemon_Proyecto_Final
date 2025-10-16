import requests
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from pokemon.models.tipo import Tipo


class TipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo
        fields = ['id', 'name']


class TipoViewSet(viewsets.ModelViewSet):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer

    def retrieve(self, request, pk=None):
        """
        Obtiene un tipo por ID o nombre desde la base de datos o desde la PokeAPI v2.
        Si no existe localmente, lo crea automáticamente.
        """
        try:
            tipo = Tipo.objects.get(pk=pk) if pk.isdigit() else Tipo.objects.get(name=pk)
            serializer = self.get_serializer(tipo)
            return Response(serializer.data)
        except Tipo.DoesNotExist:
            # Buscar el tipo en la PokeAPI
            url = f"https://pokeapi.co/api/v2/type/{pk.lower()}/"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                tipo = Tipo.objects.create(name=data["name"])
                serializer = self.get_serializer(tipo)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": "Tipo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
