import { apiRequest } from './utils';

export async function createBattle() {
  return apiRequest('batallas/', {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function getBattles() {
  return apiRequest('batallas/');
}

export async function getBattle(battleId) {
  return apiRequest(`batallas/${battleId}/`);
}

export async function performBattleAction(battleId, actionData) {
  return apiRequest(`batallas/${battleId}/accion/`, {
    method: 'POST',
    body: JSON.stringify(actionData),
  });
}

export async function attackInBattle(battleId, userPokemonId, movimientoId) {
  return performBattleAction(battleId, {
    accion: 'atacar',
    user_pokemon_id: userPokemonId,
    movimiento_id: movimientoId,
  });
}

export async function captureInBattle(battleId, userPokemonId) {
  return performBattleAction(battleId, {
    accion: 'capturar',
    user_pokemon_id: userPokemonId,
  });
}

export async function healInBattle(battleId, userPokemonId) {
  return performBattleAction(battleId, {
    accion: 'curar',
    user_pokemon_id: userPokemonId,
  });
}

export async function fleeFromBattle(battleId) {
  return performBattleAction(battleId, {
    accion: 'huir',
  });
}

export async function changePokemonInBattle(battleId, newPokemonId) {
  return performBattleAction(battleId, {
    accion: 'cambiar_pokemon',
    user_pokemon_id: newPokemonId,
  });
}