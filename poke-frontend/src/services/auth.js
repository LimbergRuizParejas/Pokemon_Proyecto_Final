const AUTH_URL = "http://localhost:8000/api/auth/"; // Ajusta si tu backend usa otra ruta base

export async function loginUser(credentials) {
  try {
    const response = await fetch(`${AUTH_URL}login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) throw new Error("Error al iniciar sesión");

    const data = await response.json();
    // Guardar token en localStorage
    localStorage.setItem("token", data.access);
    return data;
  } catch (error) {
    console.error("Error en loginUser:", error);
    return null;
  }
}

export async function registerUser(userData) {
  try {
    const response = await fetch(`${AUTH_URL}register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });

    if (!response.ok) throw new Error("Error al registrar usuario");

    return await response.json();
  } catch (error) {
    console.error("Error en registerUser:", error);
    return null;
  }
}
