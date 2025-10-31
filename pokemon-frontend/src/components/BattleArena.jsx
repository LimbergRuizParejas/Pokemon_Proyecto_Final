import { useState } from "react";
import { motion } from "framer-motion";

export default function BattleArena() {
  const [enemyHP] = useState(80);
  const [playerHP] = useState(100);
  const [log] = useState("¡Un Pokémon salvaje apareció!");
  const [showMoves, setShowMoves] = useState(false);

  const player = {
    name: "Bulbasaur",
    backSprite:
      "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png",
  };

  const enemy = {
    name: "Seel",
    frontSprite:
      "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/86.png",
  };

  const moves = ["Razor Wind", "Cut", "Bind", "Swords Dance"];

  return (
    <div
      className="relative w-[880px] h-[500px] border-4 border-blue-300 rounded-xl shadow-lg mt-24 overflow-hidden"
      style={{
        backgroundImage: "url('/src/assets/fondo-batalla.png')", // tu fondo
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* 📊 Cuadro de vida del enemigo (arriba izquierda) */}
      <div className="absolute top-10 left-25 bg-white/95 border border-gray-400 px-4 py-2 rounded-lg shadow w-80">
        <h2 className="text-lg font-bold text-gray-700">{enemy.name}</h2>
        <div className="w-full bg-gray-200 h-3 rounded mt-1">
          <div
            className="bg-green-500 h-3 rounded"
            style={{ width: `${enemyHP}%` }}
          ></div>
        </div>
      </div>

      {/* 🧊 Sprite enemigo (arriba derecha) */}
      <motion.img
        src={enemy.frontSprite}
        alt={enemy.name}
        className="absolute top-2 right-30 h-72 drop-shadow-lg"
        animate={{ y: [0, -6, 0] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      />

      {/* 🌿 Sprite jugador (abajo izquierda) */}
      <motion.img
        src={player.backSprite}
        alt={player.name}
        className="absolute bottom-15 left-20 h-80 drop-shadow-lg"
        animate={{ y: [0, 6, 0] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      />

      {/* 📊 Cuadro de vida jugador (abajo derecha, al lado del sprite) */}
      <div className="absolute bottom-40 right-30 bg-white/95 border border-gray-400 px-4 py-2 rounded-lg shadow w-80">
        <h2 className="text-lg font-bold text-gray-700">{player.name}</h2>
        <div className="w-full bg-gray-200 h-3 rounded mt-1">
          <div
            className="bg-green-500 h-3 rounded"
            style={{ width: `${playerHP}%` }}
          ></div>
        </div>
      </div>

      {/* 🕹️ Cuadro de comandos */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-white/95 border border-gray-400 rounded-lg shadow-lg w-[820px] h-[120px] grid grid-cols-2 gap-4 p-4">
        {/* Texto */}
        <div className="flex items-center justify-center border border-gray-300 rounded p-3 text-gray-800 font-medium">
          {log}
        </div>

        {/* Botones o movimientos */}
        {!showMoves ? (
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setShowMoves(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Luchar
            </button>
            <button className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
              Curar
            </button>
            <button className="bg-yellow-400 hover:bg-yellow-500 text-blue-900 font-bold py-2 px-4 rounded">
              Pokémon
            </button>
            <button className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
              Huir
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {moves.map((m) => (
              <button
                key={m}
                onClick={() => setShowMoves(false)}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded"
              >
                {m}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
