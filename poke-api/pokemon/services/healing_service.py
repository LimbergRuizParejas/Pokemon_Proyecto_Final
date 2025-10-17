from ..models import UserPokemon


class HealingService:

    @staticmethod
    def curar_todos_los_pokemon(usuario):
        pokemones = UserPokemon.objects.filter(user=usuario)

        for user_pokemon in pokemones:
            user_pokemon.current_hp = user_pokemon.pokemon.hp
            user_pokemon.save()

        return pokemones.count()

    @staticmethod
    def curar_pokemon_especifico(usuario, user_pokemon_id):
        try:
            user_pokemon = UserPokemon.objects.get(id=user_pokemon_id, user=usuario)
            user_pokemon.current_hp = user_pokemon.pokemon.hp
            user_pokemon.save()
            return user_pokemon
        except UserPokemon.DoesNotExist:
            return None

    @staticmethod
    def revivir_pokemon(usuario, user_pokemon_id):
        try:
            user_pokemon = UserPokemon.objects.get(id=user_pokemon_id, user=usuario)
            if user_pokemon.current_hp <= 0:
                hp_maximo = user_pokemon.pokemon.hp
                user_pokemon.current_hp = hp_maximo // 2
                user_pokemon.save()
                return user_pokemon
            return user_pokemon
        except UserPokemon.DoesNotExist:
            return None

    @staticmethod
    def revivir_todos_los_pokemon(usuario):
        pokemones_derrotados = UserPokemon.objects.filter(
            user=usuario,
            current_hp__lte=0
        )

        for user_pokemon in pokemones_derrotados:
            hp_maximo = user_pokemon.pokemon.hp
            user_pokemon.current_hp = hp_maximo // 2
            user_pokemon.save()

        return pokemones_derrotados.count()