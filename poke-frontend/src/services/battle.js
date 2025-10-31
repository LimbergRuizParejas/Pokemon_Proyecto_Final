const API_URL = "http://localhost:8000/api/pokemon/";

export const postCapturePokemon = async (pokemonName) => {
  const token = localStorage.getItem("token");
  try {
    const res = await fetch(`${API_URL}capturar/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: token ? `Bearer ${token}` : "",
      },
      body: JSON.stringify({ name: pokemonName }),
    });
    return res;
  } catch (error) {
    console.error("Error al capturar Pokémon:", error);
    return null;
  }
};
