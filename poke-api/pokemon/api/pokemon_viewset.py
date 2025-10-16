from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from pokemon.models import Pokemon


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