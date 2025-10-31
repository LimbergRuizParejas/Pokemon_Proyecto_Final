import { useState } from "react";
import { registerUser } from "../services/auth.js";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (form.password !== form.password2) {
      setError("Las contraseñas no coinciden ⚠️");
      return;
    }

    const result = await registerUser({
      username: form.username,
      email: form.email,
      password: form.password,
    });

    if (result) {
      setSuccess("Registro exitoso 🎉 Redirigiendo al login...");
      setTimeout(() => navigate("/login"), 2000);
    } else {
      setError("Error al registrarse. Intenta nuevamente.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 via-yellow-50 to-white">
      <div className="bg-white/90 shadow-lg rounded-2xl p-8 w-96 border border-blue-200">
        <h1 className="text-3xl font-extrabold text-center text-blue-700 mb-6">
          Crear Cuenta
        </h1>

        {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
        {success && <p className="text-green-500 text-sm text-center mb-4">{success}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            name="username"
            placeholder="Nombre de usuario"
            value={form.username}
            onChange={handleChange}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400"
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Correo electrónico"
            value={form.email}
            onChange={handleChange}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Contraseña"
            value={form.password}
            onChange={handleChange}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400"
            required
          />
          <input
            type="password"
            name="password2"
            placeholder="Repetir contraseña"
            value={form.password2}
            onChange={handleChange}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400"
            required
          />

          <button
            type="submit"
            className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Registrarse
          </button>
        </form>

        <p className="text-center text-gray-600 mt-4 text-sm">
          ¿Ya tienes cuenta?{" "}
          <a href="/login" className="text-blue-600 font-medium hover:underline">
            Inicia sesión
          </a>
        </p>
      </div>
    </div>
  );
}
