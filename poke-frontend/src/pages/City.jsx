import Navbar from "../components/Navbar";

export default function City() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-yellow-50 text-gray-800 flex flex-col items-center pt-32">
      <Navbar />
      <header className="text-center mt-10">
        <h1 className="text-5xl font-extrabold text-blue-700 drop-shadow-md mb-4">
          🌆 Ciudad Pokémon
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          ¡Bienvenido entrenador! En este mundo podrás capturar Pokémon,
          combatir con ellos y convertirte en el mejor.  
          <br />
          <span className="text-yellow-600 font-semibold">
            Inicia sesión o regístrate
          </span>{" "}
          para comenzar tu aventura.
        </p>
      </header>

      <footer className="mt-20 text-gray-500 text-sm">
        Proyecto Gamificación •{" "}
        <span className="text-blue-600 font-semibold">PokeAPI</span>
      </footer>
    </div>
  );
}
