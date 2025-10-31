import { apiRequest } from './utils';

export async function getPokemonStatus() {
  return apiRequest('centro-pokemon/estado/');
}

export async function healAllPokemon() {
  return apiRequest('centro-pokemon/curar_todos/', {
    method: 'POST',
  });
}

export async function healPokemon(userPokemonId) {
  return apiRequest('centro-pokemon/curar/', {
    method: 'POST',
    body: JSON.stringify({ user_pokemon_id: userPokemonId }),
  });
}

export async function reviveAllPokemon() {
  return apiRequest('centro-pokemon/revivir_todos/', {
    method: 'POST',
  });
}

export async function revivePokemon(userPokemonId) {
  return apiRequest('centro-pokemon/revivir/', {
    method: 'POST',
    body: JSON.stringify({ user_pokemon_id: userPokemonId }),
  });
}