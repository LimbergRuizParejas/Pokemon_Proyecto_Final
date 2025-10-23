import { useEffect, useState } from "react";
import { getTipos } from "../services/api";
import Navbar from "../components/Navbar";

/**
 * 🌆 City.jsx
 * Página principal que muestra los tipos elementales de Pokémon.
 * Consume el endpoint /api/pokemon/tipos/ desde getTipos()
 * y presenta tarjetas visuales interactivas.
 */
export default function City() {
  const [types, setTypes] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🔄 Cargar tipos al iniciar
  useEffect(() => {
    const fetchTipos = async () => {
      try {
        const data = await getTipos();
        setTypes(data || []);
      } catch (error) {
        console.error("Error al obtener tipos:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTipos();
  }, []);

  // 🌀 Pantalla de carga
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-blue-50 via-yellow-50 to-blue-100">
        <Navbar />
        <p className="text-xl text-blue-600 animate-pulse font-semibold mt-10">
          Cargando tipos de Pokémon...
        </p>
      </div>
    );
  }

  // 🎨 Función auxiliar para definir colores según tipo
  const colorForType = (typeName) => {
    const colors = {
      fuego: "text-red-500",
      agua: "text-blue-500",
      planta: "text-green-600",
      eléctrico: "text-yellow-400",
      tierra: "text-yellow-600",
      hielo: "text-cyan-400",
      lucha: "text-orange-500",
      veneno: "text-purple-500",
      volador: "text-sky-500",
      roca: "text-stone-500",
      psíquico: "text-pink-500",
      dragón: "text-indigo-600",
      siniestro: "text-gray-700",
      hada: "text-pink-400",
    };
    return colors[typeName?.toLowerCase()] || "text-gray-700";
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-yellow-50 text-gray-800 flex flex-col items-center pb-10">
      <Navbar />

      {/* 🏙️ Encabezado */}
      <header className="mt-32 mb-10 text-center">
        <h1 className="text-5xl font-extrabold text-blue-700 drop-shadow-md mb-2">
          Ciudad Pokémon
        </h1>
        <p className="text-gray-600 text-lg">
          Explora los tipos elementales del mundo Pokémon
        </p>
      </header>

      {/* 🧩 Contenedor de tipos */}
      {types.length === 0 ? (
        <p className="text-gray-600 text-center text-lg">
          No hay tipos de Pokémon registrados aún 🌀
        </p>
      ) : (
        <div className="grid gap-6 w-full max-w-6xl px-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {types.map((tipo) => (
            <div
              key={tipo.id}
              className="relative bg-white/80 backdrop-blur-sm border border-blue-200 rounded-2xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-200"
            >
              <h2
                className={`text-2xl font-bold text-center capitalize mb-2 ${colorForType(
                  tipo.name
                )}`}
              >
                {tipo.name}
              </h2>
              <div className="flex justify-center">
                <span className="text-sm text-gray-500 italic">
                  Tipo elemental
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 🦶 Footer */}
      <footer className="mt-16 text-gray-500 text-sm">
        Proyecto de Gamificación —{" "}
        <span className="text-blue-600 font-semibold">PokeAPI</span> ©2025
      </footer>
    </div>
  );
}
