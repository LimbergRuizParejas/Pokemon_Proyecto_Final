import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext.jsx";
import Navbar from "../components/Navbar";

export default function City() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const token = localStorage.getItem("token");

  return (

    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-sky-200 to-blue-100 p-6 text-center">
          <Navbar />
      <h1 className="text-5xl font-extrabold text-blue-800 drop-shadow-md mb-6">
        🌆 Bienvenido a PokeCity
      </h1>
      <p className="max-w-2xl text-lg text-gray-700 mb-10">
        Esta es tu base de entrenamiento. Desde aquí podrás capturar Pokémon salvajes, 
        participar en batallas y administrar tu equipo. Recuerda que solo puedes tener 
        <span className="font-semibold text-blue-600"> 10 Pokémon</span> capturados y 
        <span className="font-semibold text-blue-600"> 6 en tu equipo activo</span>.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <button
          onClick={() => navigate("/capture")}
          className="bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-8 rounded-xl shadow-md transition-transform transform hover:scale-105"
        >
          🎯 Capturar Pokémon
        </button>

        <button
          onClick={() => navigate("/battle")}
          className="bg-red-500 hover:bg-red-600 text-white font-bold py-4 px-8 rounded-xl shadow-md transition-transform transform hover:scale-105"
        >
          ⚔️ Enfrentamientos
        </button>

        <button
          onClick={() => navigate("/dashboard")}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-4 px-8 rounded-xl shadow-md transition-transform transform hover:scale-105"
        >
          📋 Mi Equipo
        </button>
      </div>

      <div className="text-gray-600 text-sm mt-4">
        {!token ? (
          <div>
            <p>¿Aún no tienes cuenta?</p>
            <div className="space-x-4 mt-2">
              <button
                onClick={() => navigate("/register")}
                className="text-blue-600 font-medium hover:underline"
              >
                Registrarme
              </button>
              <button
                onClick={() => navigate("/login")}
                className="text-blue-600 font-medium hover:underline"
              >
                Iniciar sesión
              </button>
            </div>
          </div>
        ) : (
          <p className="text-blue-700 font-medium">
            ¡Hola <span className="font-semibold">{user?.username || "Entrenador"}</span>!  
            Estás listo para comenzar tu aventura.
          </p>
        )}
      </div>
    </div>
  );
}
