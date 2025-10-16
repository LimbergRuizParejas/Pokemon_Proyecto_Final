from django.db import models


class Tipo(models.Model):
    name = models.CharField(max_length=50, unique=True)
    damage_relations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tipos'

    def calcular_multiplicador_danio(self, tipo_ataque_nombre):
        if not self.damage_relations or not isinstance(self.damage_relations, dict):
            return 1.0

        relaciones = self.damage_relations
        multiplicador = 1.0

        if 'double_damage_from' in relaciones:
            if any(tipo == tipo_ataque_nombre for tipo in relaciones['double_damage_from']):
                multiplicador *= 2.0

        if 'half_damage_from' in relaciones:
            if any(tipo == tipo_ataque_nombre for tipo in relaciones['half_damage_from']):
                multiplicador *= 0.5

        if 'no_damage_from' in relaciones:
            if any(tipo == tipo_ataque_nombre for tipo in relaciones['no_damage_from']):
                multiplicador *= 0.0

        return multiplicador
