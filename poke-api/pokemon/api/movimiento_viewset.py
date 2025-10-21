import requests
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from pokemon.models.movimiento import Movimiento
from pokemon.models.tipo import Tipo


class TipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo
        fields = ['id', 'name']


class MovimientoSerializer(serializers.ModelSerializer):
    tipo = TipoSerializer(read_only=True)

    class Meta:
        model = Movimiento
        fields = ['id', 'name', 'power', 'pp', 'accuracy', 'tipo']


class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer

    def retrieve(self, request, pk=None):
        """
        Obtiene un movimiento por ID o nombre desde la base de datos o desde la PokeAPI v2.
        Si no existe localmente, lo crea automáticamente junto con su tipo si es necesario.
        """
        try:
            movimiento = Movimiento.objects.get(pk=pk) if pk.isdigit() else Movimiento.objects.get(name=pk)
            serializer = self.get_serializer(movimiento)
            return Response(serializer.data)
        except Movimiento.DoesNotExist:
            # Buscar en la PokeAPI
            url = f"https://pokeapi.co/api/v2/move/{pk.lower()}/"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()

                # Buscar o crear tipo asociado
                tipo_name = data["type"]["name"]
                tipo, _ = Tipo.objects.get_or_create(name=tipo_name)

                # Crear el movimiento
                movimiento = Movimiento.objects.create(
                    name=data["name"],
                    power=data["power"],
                    pp=data["pp"],
                    accuracy=data["accuracy"],
                    tipo=tipo
                )
                serializer = self.get_serializer(movimiento)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response({"error": "Movimiento no encontrado"}, status=status.HTTP_404_NOT_FOUND)
