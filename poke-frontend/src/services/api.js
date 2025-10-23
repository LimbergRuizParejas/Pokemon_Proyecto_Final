// src/services/api.js

import axios from "axios";

// ✅ Configuración base del cliente API
export const api = axios.create({
  baseURL: "http://localhost:8000/api/",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 segundos de límite de espera
});

// 🧠 Interceptor de errores global (para debugging y control central)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("❌ Error en solicitud API:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/* =======================================================
   FUNCIONES ESPECÍFICAS DE POKÉMON
======================================================= */

/**
 * 🔹 Obtener todos los Pokémon
 * GET /api/pokemon/
 */
export async function getPokemons() {
  try {
    const res = await api.get("pokemon/");
    return res.data;
  } catch (error) {
    console.error("⚠️ Error al obtener los Pokémon:", error);
    return [];
  }
}

/**
 * 🔹 Obtener Pokémon por ID
 * GET /api/pokemon/:id/
 */
export async function getPokemonById(id) {
  try {
    const res = await api.get(`pokemon/${id}/`);
    return res.data;
  } catch (error) {
    console.error(`⚠️ Error al obtener el Pokémon con ID ${id}:`, error);
    return null;
  }
}

/**
 * 🔹 Obtener Pokémon aleatorio
 * GET /api/pokemon/random/
 */
export async function getRandomPokemon() {
  try {
    const res = await api.get("pokemon/random/");
    return res.data;
  } catch (error) {
    console.error("⚠️ Error al obtener Pokémon aleatorio:", error);
    return null;
  }
}

/**
 * 🔹 Obtener tipos de Pokémon
 * GET /api/pokemon/tipos/
 */
export async function getTipos() {
  try {
    const res = await api.get("pokemon/tipos/");
    return res.data;
  } catch (error) {
    console.error("⚠️ Error al obtener los tipos:", error);
    return [];
  }
}

/**
 * 🔹 Crear un nuevo Pokémon
 * POST /api/pokemon/
 */
export async function createPokemon(pokemonData) {
  try {
    const res = await api.post("pokemon/", pokemonData);
    return res.data;
  } catch (error) {
    console.error("⚠️ Error al crear Pokémon:", error);
    return null;
  }
}

/**
 * 🔹 Actualizar un Pokémon existente
 * PUT /api/pokemon/:id/
 */
export async function updatePokemon(id, pokemonData) {
  try {
    const res = await api.put(`pokemon/${id}/`, pokemonData);
    return res.data;
  } catch (error) {
    console.error("⚠️ Error al actualizar Pokémon:", error);
    return null;
  }
}

/**
 * 🔹 Eliminar un Pokémon
 * DELETE /api/pokemon/:id/
 */
export async function deletePokemon(id) {
  try {
    await api.delete(`pokemon/${id}/`);
    return true;
  } catch (error) {
    console.error("⚠️ Error al eliminar Pokémon:", error);
    return false;
  }
}

/* =======================================================
   FUNCIONES GENERALES (puedes ampliar más adelante)
======================================================= */

/**
 * 🧩 Ping del servidor (verificar conexión)
 */
export async function checkServer() {
  try {
    const res = await api.get("pokemon/");
    console.log("✅ Servidor API en línea");
    return res.status === 200;
  } catch (error) {
    console.error("❌ No se pudo conectar con la API:", error.message);
    return false;
  }
}
