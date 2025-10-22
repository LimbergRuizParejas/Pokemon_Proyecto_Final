import { useEffect, useState } from "react";
import { getTipos } from "../services/api";
import Navbar from "../components/Navbar";

export default function City() {
  const [types, setTypes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTipos = async () => {
      const data = await getTipos();
      setTypes(data);
      setLoading(false);
    };
    fetchTipos();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 via-yellow-50 to-blue-100">
        <p className="text-xl text-blue-600 animate-pulse font-medium">
          Cargando tipos...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-yellow-50 text-gray-800 flex flex-col items-center pt-36 pb-10">
      <Navbar />
      <header className="mb-10 text-center">
        <h1 className="text-5xl font-extrabold text-blue-700 drop-shadow-md mb-2">
          Ciudad Pokémon
        </h1>
        <p className="text-gray-600 text-lg">
          Explora los tipos elementales disponibles en el mundo Pokémon
        </p>
      </header>
      {/* Contenedor de tarjetas */}
      {types.length === 0 ? (
        <p className="text-gray-600 text-center text-lg">
          No hay tipos de Pokémon registrados aún 🌀
        </p>
      ) : (
        <div className="grid gap-6 w-full max-w-6xl px-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {types.map((tipo) => (
            <div
              key={tipo.id}
              className="relative bg-white/80 backdrop-blur-sm border border-blue-200 rounded-2xl p-6 shadow-md hover:shadow-lg hover:scale-105 transition-transform duration-200"
            >
              <h2
                className={`text-2xl font-bold text-center capitalize mb-2 ${
                  tipo.name === "Fuego"
                    ? "text-red-500"
                    : tipo.name === "Agua"
                    ? "text-blue-500"
                    : tipo.name === "Planta"
                    ? "text-green-600"
                    : tipo.name === "Eléctrico"
                    ? "text-yellow-400"
                    : tipo.name === "Tierra"
                    ? "text-yellow-600"
                    : tipo.name === "Hielo"
                    ? "text-cyan-400"
                    : tipo.name === "Lucha"
                }`}
              >
                {tipo.name}
              </h2>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <footer className="mt-16 text-gray-500 text-sm">
        Proyecto Gamificación • <span className="text-blue-600 font-semibold">PokeAPI</span>
      </footer>
    </div>
  );
}
