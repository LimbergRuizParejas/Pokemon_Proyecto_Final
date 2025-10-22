const API_URL = "http://localhost:8000/api/pokemon/";

export async function getTipos() {
  try {
    const response = await fetch(`${API_URL}tipos/`);
    if (!response.ok) {
      throw new Error("Error al obtener los tipos");
    }
    return await response.json();
  } catch (error) {
    console.error("Error en getTipos:", error);
    return [];
  }
}
