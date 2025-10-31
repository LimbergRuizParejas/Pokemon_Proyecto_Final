const API_URL = "http://localhost:8000/api/pokemon/";

export const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export async function getInitialOptions() {
  try {
    const res = await fetch(`${API_URL}seleccion-inicial/opciones/`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Error al obtener los Pokémon iniciales");
    return await res.json();
  } catch (err) {
    console.error("getInitialOptions:", err);
    return [];
  }
}

export async function chooseInitialPokemon(nombre_pokemon) {
  try {
    const res = await fetch(`${API_URL}seleccion-inicial/elegir/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ nombre_pokemon }),
    });
    return res;
  } catch (err) {
    console.error("chooseInitialPokemon:", err);
    return null;
  }
}
