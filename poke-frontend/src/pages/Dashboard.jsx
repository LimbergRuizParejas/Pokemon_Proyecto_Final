import { useEffect, useState, useContext } from "react";
import Navbar from "../components/Navbar";
import { AuthContext } from "../context/AuthContext.jsx";
import { useNavigate } from "react-router-dom";
import { getUserPokemons, changePokemonTeamStatus } from "../services/pokemonManagement.js";
import { healAllPokemon } from "../services/healing.js";

export default function Dashboard() {
  const [pokemons, setPokemons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [healing, setHealing] = useState(false);
  const [changing, setChanging] = useState(null); 
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const fetchPokemons = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token || !user) {
        navigate("/login");
        return;
      }

      const data = await getUserPokemons();

      const equipo = (data.equipo || []).map((p, idx) => ({
        ...p,
        origen: "equipo",
        posicion: idx + 1,
      }));

      const reserva = (data.reserva || []).map((p) => ({
        ...p,
        origen: "reserva",
      }));

      setPokemons([...equipo, ...reserva]);
    } catch (err) {
      console.error("❌ Error al cargar Pokémon:", err);
      setError("No se pudieron cargar tus Pokémon 😢");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPokemons();
  }, [navigate, user]);

  const handleHealAll = async () => {
    try {
      setHealing(true);
      await healAllPokemon();
      await fetchPokemons();
      alert("✨ ¡Todos tus Pokémon han sido curados!");
    } catch (err) {
      console.error("❌ Error al curar Pokémon:", err);
      alert("No se pudieron curar tus Pokémon 😢");
    } finally {
      setHealing(false);
    }
  };

  const handleChangeTeamStatus = async (userPokemonId) => {
    try {
      setChanging(userPokemonId);
      await changePokemonTeamStatus(userPokemonId);
      await fetchPokemons();
    } catch (err) {
      console.error("❌ Error al cambiar Pokémon de equipo:", err);
      alert("No se pudo mover el Pokémon 😢");
    } finally {
      setChanging(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-yellow-100 flex flex-col items-center pt-24">
      <Navbar />
      <br />

      <h1 className="text-4xl font-extrabold text-blue-700 mb-4 drop-shadow-md">
        Mis Pokémon Capturados
      </h1>

      <button
        onClick={handleHealAll}
        disabled={healing}
        className={`mb-8 px-8 py-3 rounded-xl font-semibold text-white transition-all shadow-md
          ${healing ? "bg-green-400 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"}`}
      >
        {healing ? "Curando..." : "Ir al Centro Pokémon"}
      </button>

      {loading ? (
        <p className="text-blue-600 animate-pulse">Cargando tus Pokémon...</p>
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : pokemons.length === 0 ? (
        <p className="text-gray-600 text-lg">Aún no has capturado ningún Pokémon 😢</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 w-full max-w-6xl px-6 pb-10">
          {pokemons.map((p) => (
            <div
              key={p.user_pokemon_id}
              className="relative bg-white/80 backdrop-blur-md border border-blue-100 rounded-2xl p-4 shadow-md flex flex-col items-center transition-transform duration-200 hover:scale-105"
            >
              <span
                className={`absolute top-2 right-2 px-2 py-1 text-xs font-semibold rounded-full ${
                  p.origen === "equipo"
                    ? "bg-green-100 text-green-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}
              >
                {p.origen === "equipo" ? `Equipo #${p.posicion}` : "Reserva"}
              </span>

              {p.pokemon?.sprites?.front_default ? (
                <img
                  src={p.pokemon.sprites.front_default}
                  alt={p.pokemon.name}
                  className="h-32 w-32 object-contain mb-3"
                />
              ) : (
                <div className="h-32 w-32 flex items-center justify-center text-gray-400">
                  ❌ Sin imagen
                </div>
              )}

              <h2 className="text-2xl font-semibold capitalize text-blue-700 mb-2">
                {p.pokemon?.name}
              </h2>

              <div className="flex flex-wrap justify-center gap-2 mb-2">
                {p.pokemon?.tipos?.map((tipo) => (
                  <span
                    key={tipo}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium capitalize"
                  >
                    {tipo}
                  </span>
                ))}
              </div>

              <p className="text-sm text-gray-600">
                <strong>Nivel:</strong> {p.nivel}
              </p>
              <p className="text-sm text-gray-600">
                <strong>HP actual:</strong> {p.current_hp}/{p.pokemon.stats.hp}
              </p>

              {p.origen === "reserva" && (
                <button
                  onClick={() => handleChangeTeamStatus(p.user_pokemon_id)}
                  disabled={changing === p.user_pokemon_id}
                  className={`mt-2 px-4 py-2 rounded-lg text-white font-semibold transition-all shadow-md
                    ${changing === p.user_pokemon_id ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"}`}
                >
                  {changing === p.user_pokemon_id ? "Moviendo..." : "Pasar a Equipo"}
                </button>
              )}

              {p.origen === "equipo" && (
                <button
                  onClick={() => handleChangeTeamStatus(p.user_pokemon_id)}
                  disabled={changing === p.user_pokemon_id}
                  className={`mt-2 px-4 py-2 rounded-lg text-white font-semibold transition-all shadow-md
                    ${changing === p.user_pokemon_id ? "bg-red-400 cursor-not-allowed" : "bg-red-600 hover:bg-red-700"}`}
                >
                  {changing === p.user_pokemon_id ? "Moviendo..." : "Enviar a Reserva"}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
