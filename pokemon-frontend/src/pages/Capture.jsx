import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";

export default function Capture() {
  const [pokemon, setPokemon] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const getRandomPokemon = async () => {
    try {
      setLoading(true);
      setMessage("");
      const randomId = Math.floor(Math.random() * 151) + 1;
      const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${randomId}`);
      const data = await res.json();
      setPokemon({
        id: data.id,
        name: data.name,
        sprite: data.sprites.other["official-artwork"].front_default,
        hp: data.stats[0].base_stat,
        attack: data.stats[1].base_stat,
        defense: data.stats[2].base_stat,
        type: data.types[0].type.name,
      });
    } catch (error) {
      console.error("Error al obtener Pokémon:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCapture = () => {
    const success = Math.random() < 0.6; // 60% probabilidad de captura
    if (success) {
      setMessage(`🎉 ¡Capturaste a ${pokemon.name.toUpperCase()}!`);
      // Aquí luego podrías hacer POST al backend para guardarlo
    } else {
      setMessage(`😢 ${pokemon.name.toUpperCase()} escapó...`);
    }
  };

  useEffect(() => {
    getRandomPokemon();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-blue-100 flex flex-col items-center pt-32">
      <Navbar />
      <h1 className="text-4xl font-extrabold text-blue-700 mb-6 drop-shadow-md">
        ¡Atrapa tu Pokémon!
      </h1>

      {loading ? (
        <p className="text-lg text-blue-600 animate-pulse">Buscando Pokémon...</p>
      ) : pokemon ? (
        <div className="bg-white/80 backdrop-blur-md p-8 rounded-2xl shadow-lg w-80 flex flex-col items-center text-center">
          <img
            src={pokemon.sprite}
            alt={pokemon.name}
            className="h-40 w-40 object-contain mb-4 drop-shadow-lg"
          />
          <h2 className="text-3xl font-bold capitalize text-blue-700 mb-2">
            {pokemon.name}
          </h2>
          <p className="text-gray-600 mb-4 capitalize">
            Tipo: <span className="font-semibold text-yellow-600">{pokemon.type}</span>
          </p>

          <div className="text-sm text-gray-700 mb-4">
            <p>❤️ HP: {pokemon.hp}</p>
            <p>⚔️ Ataque: {pokemon.attack}</p>
            <p>🛡️ Defensa: {pokemon.defense}</p>
          </div>

          <button
            onClick={handleCapture}
            className="bg-yellow-400 hover:bg-yellow-500 text-blue-900 font-bold py-2 px-6 rounded-full shadow transition-transform transform hover:scale-105"
          >
            Atrapar
          </button>

          {message && (
            <p
              className={`mt-4 font-semibold ${
                message.includes("🎉") ? "text-green-600" : "text-red-500"
              }`}
            >
              {message}
            </p>
          )}

          <button
            onClick={getRandomPokemon}
            className="mt-4 text-blue-600 underline hover:text-blue-800 transition"
          >
            🔄 Buscar otro Pokémon
          </button>
        </div>
      ) : (
        <p className="text-gray-600">No se pudo cargar el Pokémon.</p>
      )}
    </div>
  );
}
