import { apiRequest } from './utils';

export async function getUserPokemons() {
  return apiRequest('mis-pokemones/');
}

export async function getTeam() {
  return apiRequest('mis-pokemones/equipo/');
}

export async function getReserve() {
  return apiRequest('mis-pokemones/reserva/');
}

export async function changePokemonTeamStatus(userPokemonId) {
  return apiRequest(`mis-pokemones/${userPokemonId}/cambiar_equipo/`, {
    method: 'POST',
  });
}

export async function releasePokemon(userPokemonId) {
  return apiRequest(`mis-pokemones/${userPokemonId}/liberar/`, {
    method: 'POST',
  });
}

export async function swapPokemons(pokemonEquipoId, pokemonReservaId) {
  return apiRequest('mis-pokemones/intercambiar/', {
    method: 'POST',
    body: JSON.stringify({
      pokemon_equipo_id: pokemonEquipoId,
      pokemon_reserva_id: pokemonReservaId,
    }),
  });
}

export async function replaceTeamPokemon(pokemonSaleId, pokemonEntraId) {
  return apiRequest('mis-pokemones/reemplazar_en_equipo/', {
    method: 'POST',
    body: JSON.stringify({
      pokemon_sale_id: pokemonSaleId,
      pokemon_entra_id: pokemonEntraId,
    }),
  });
}