import { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { getInitialOptions, chooseInitialPokemon } from "../services/pokemon";
import { AuthContext } from "../context/AuthContext.jsx";

export default function SelectStarter() {
  const [starters, setStarters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  useEffect(() => {
    const fetchStarters = async () => {
      setLoading(true);
      try {
        const data = await getInitialOptions();

        console.log("⚡ Datos recibidos del backend:", data);

        let names = [];
        if (Array.isArray(data)) {
          names = data.map((p) => (typeof p === "string" ? p : p.nombre || p.name));
        } else if (data.opciones) {
          names = data.opciones.map((p) => p.nombre || p.name);
        } else if (data.results) {
          names = data.results.map((p) => p.name);
        } else {
          console.warn("❌ Formato inesperado del backend:", data);
        }

        names = names.filter(Boolean);

        const withSprites = await Promise.all(
          names.map(async (name) => {
            try {
              const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${name}`);
              if (!res.ok) throw new Error(`No se encontró sprite para ${name}`);
              const pokeData = await res.json();
              return {
                name,
                sprite: pokeData.sprites.other["official-artwork"].front_default,
              };
            } catch (err) {
              console.error(`Error cargando sprite de ${name}:`, err);
              return { name, sprite: null };
            }
          })
        );

        setStarters(withSprites);
      } catch (err) {
        console.error("❌ Error general al obtener Pokémon:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStarters();
  }, []);

  const handleSelect = async (pokemonName) => {
    setSelected(pokemonName);
    setMessage("Procesando elección...");

    try {
      const res = await chooseInitialPokemon(pokemonName);
      if (!res) throw new Error("Sin respuesta del servidor");

      const data = await res.json();
      console.log("📦 Respuesta del backend al elegir:", data);

      if (res.ok) {
        setMessage(`🎉 ¡Has elegido a ${pokemonName.toUpperCase()} como tu Pokémon inicial!`);

        setTimeout(() => {
          navigate("/battle", { replace: true }); 
        }, 1500);
      } else if (res.status === 401) {
        setMessage("⚠️ Tu sesión expiró, por favor vuelve a iniciar sesión");
        setTimeout(() => navigate("/login"), 1500);
      } else {
        console.error("Error en elección:", data);
        setMessage(`⚠️ ${data.error || "No se pudo registrar tu elección"}`);
      }
    } catch (err) {
      console.error("❌ Error en handleSelect:", err);
      setMessage("⚠️ No se pudo conectar al servidor");
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token || !user) {
      navigate("/login");
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-blue-100 flex flex-col items-center pt-28">
      <Navbar />

      <h1 className="text-4xl font-extrabold text-blue-700 mb-8 drop-shadow-md">
        ¡Elige tu Pokémon inicial!
      </h1>

      {loading ? (
        <p className="text-blue-600 animate-pulse">Cargando opciones...</p>
      ) : starters.length === 0 ? (
        <p className="text-red-600">No se encontraron Pokémon iniciales 😢</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 w-full max-w-4xl px-6">
          {starters.map((poke) => (
            <div
              key={poke.name}
              onClick={() => handleSelect(poke.name)}
              className={`cursor-pointer bg-white/80 backdrop-blur-md border rounded-2xl p-6 shadow-md flex flex-col items-center transition-transform duration-200 hover:scale-105 ${
                selected === poke.name ? "border-yellow-400 shadow-yellow-300" : "border-blue-100"
              }`}
            >
              {poke.sprite ? (
                <img
                  src={poke.sprite}
                  alt={poke.name}
                  className="h-32 w-32 object-contain mb-4"
                />
              ) : (
                <div className="h-32 w-32 flex items-center justify-center text-gray-400">
                  ❌ Sin imagen
                </div>
              )}
              <h2 className="text-2xl font-semibold capitalize text-blue-700">
                {poke.name}
              </h2>
            </div>
          ))}
        </div>
      )}

      {message && (
        <p
          className={`mt-6 text-center font-semibold ${
            message.includes("🎉") ? "text-green-600" : "text-red-500"
          }`}
        >
          {message}
        </p>
      )}
    </div>
  );
}
