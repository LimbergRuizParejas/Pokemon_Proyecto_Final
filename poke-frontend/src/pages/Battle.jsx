
/* eslint-disable no-unused-vars */
import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "../services/api";

export default function Battle() {
  const [player, setPlayer] = useState(null);
  const [enemy, setEnemy] = useState(null);
  const [log, setLog] = useState([]);
  const [winner, setWinner] = useState(null);
  const [healsLeft, setHealsLeft] = useState(2);
  const [loading, setLoading] = useState(true);
  const [captured, setCaptured] = useState(false);
  const [capturedCount, setCapturedCount] = useState(0);
  const [shakePlayer, setShakePlayer] = useState(false);
  const [shakeEnemy, setShakeEnemy] = useState(false);

  const navigate = useNavigate();

  // 🧩 Tipos y efectividades (memoizado)
  const typeChart = useMemo(
    () => ({
      fire: { strong: ["grass", "bug"], weak: ["water", "rock"] },
      water: { strong: ["fire", "rock"], weak: ["electric", "grass"] },
      grass: { strong: ["water", "rock"], weak: ["fire", "ice"] },
      electric: { strong: ["water", "flying"], weak: ["ground"] },
    }),
    []
  );

  // ⚡ Cálculo de daño
  const calculateDamage = useCallback(
    (attacker, defender) => {
      let dmg = Math.floor(Math.random() * (attacker.attack / 2)) + 5;
      const atkType = attacker.type?.toLowerCase() || "normal";
      const defType = defender.type?.toLowerCase() || "normal";

      if (typeChart[atkType]?.strong.includes(defType)) dmg *= 1.5;
      if (typeChart[atkType]?.weak.includes(defType)) dmg *= 0.75;

      return Math.round(dmg);
    },
    [typeChart]
  );

  // 🧠 Obtener Pokémon aleatorios
  const getRandomPokemons = useCallback(async () => {
    try {
      setLoading(true);
      const [res1, res2] = await Promise.all([
        api.get("/pokemon/random/"),
        api.get("/pokemon/random/"),
      ]);

      const playerData = {
        ...res1.data,
        hp: res1.data.hp * 5,
        max_hp: res1.data.hp * 5,
      };
      const enemyData = {
        ...res2.data,
        hp: res2.data.hp * 5,
        max_hp: res2.data.hp * 5,
      };

      setPlayer(playerData);
      setEnemy(enemyData);
      setWinner(null);
      setCaptured(false);
      setHealsLeft(2);
      setLog([
        `⚔️ ¡Comienza la batalla entre ${playerData.name} y ${enemyData.name}!`,
      ]);
    } catch (err) {
      console.error("Error al obtener Pokémon:", err);
      setLog(["❌ Error al cargar los Pokémon."]);
    } finally {
      setLoading(false);
    }
  }, []);

  // ⚔️ Turnos de batalla
  const performRound = useCallback(() => {
    if (winner || !player || !enemy) return;

    const playerDmg = calculateDamage(player, enemy);
    const newEnemyHP = Math.max(0, enemy.hp - playerDmg);

    setShakeEnemy(true);
    setEnemy((prev) => ({ ...prev, hp: newEnemyHP }));
    setLog((prev) => [...prev, `💥 ${player.name} atacó e hizo ${playerDmg} de daño.`]);
    setTimeout(() => setShakeEnemy(false), 300);

    if (newEnemyHP <= 0) {
      setWinner("Jugador");
      setLog((prev) => [...prev, "🏆 ¡Has ganado la batalla!"]);
      return;
    }

    // Turno del enemigo
    setTimeout(() => {
      const enemyDmg = calculateDamage(enemy, player);
      const newPlayerHP = Math.max(0, player.hp - enemyDmg);

      setShakePlayer(true);
      setPlayer((prev) => ({ ...prev, hp: newPlayerHP }));
      setLog((prev) => [
        ...prev,
        `⚡ ${enemy.name} contraatacó e hizo ${enemyDmg} de daño.`,
      ]);
      setTimeout(() => setShakePlayer(false), 300);

      if (newPlayerHP <= 0) {
        setWinner("Enemigo");
        setLog((prev) => [...prev, "💀 Has sido derrotado..."]);
      }
    }, 1000);
  }, [winner, player, enemy, calculateDamage]);

  // 🧪 Curarse
  const heal = useCallback(() => {
    if (!player || healsLeft <= 0 || winner) return;

    const healAmount = Math.floor(Math.random() * 25) + 15;
    const newHP = Math.min(player.max_hp, player.hp + healAmount);

    setPlayer({ ...player, hp: newHP });
    setHealsLeft((prev) => prev - 1);
    setLog((prev) => [
      ...prev,
      `🧪 ${player.name} se curó ${healAmount} HP (${healsLeft - 1} curas restantes).`,
    ]);
  }, [player, healsLeft, winner]);

  // 🎯 Capturar Pokémon enemigo
  const capturePokemon = useCallback(async () => {
    if (capturedCount >= 10) {
      setLog((prev) => [
        ...prev,
        "🚫 Ya tienes el máximo de 10 Pokémon capturados.",
      ]);
      return;
    }

    try {
      const res = await api.post("/pokemon/capturar/", { name: enemy.name });
      if (res.status === 201 || res.status === 200) {
        setCaptured(true);
        setCapturedCount((prev) => prev + 1);
        setLog((prev) => [...prev, `🎯 ¡Has capturado a ${enemy.name}!`]);
      } else {
        setLog((prev) => [...prev, "⚠️ No se pudo capturar el Pokémon."]);
      }
    } catch (err) {
      console.error(err);
      setLog((prev) => [
        ...prev,
        "❌ Error al capturar (¿quizás ya tienes 10 Pokémon?)",
      ]);
    }
  }, [enemy, capturedCount]);

  // 🚀 Cargar al iniciar
  useEffect(() => {
    getRandomPokemons();
  }, [getRandomPokemons]);

  // 🕓 Pantalla de carga
  if (loading || !player || !enemy) {
    return (
      <div className="flex items-center justify-center h-screen text-xl font-semibold">
        Cargando batalla...
      </div>
    );
  }

  // 🎨 Render principal
  return (
    <div className="flex flex-col items-center p-6 min-h-screen bg-gradient-to-b from-blue-50 to-purple-100">
      <motion.h1
        initial={{ y: -30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="text-3xl font-extrabold text-center mb-4"
      >
        ⚔️ Pokémon de batalla ⚔️
      </motion.h1>

      <p className="text-sm text-gray-600 mb-4">
        Pokémon capturados: <b>{capturedCount}</b> / 10
      </p>

      {/* 🧩 Campo de batalla */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
        {/* Jugador */}
        <motion.div
          animate={shakePlayer ? { x: [-8, 8, -8, 8, 0] } : {}}
          transition={{ duration: 0.3 }}
          className={`p-4 rounded-2xl shadow-lg flex flex-col items-center ${
            winner === "Jugador"
              ? "bg-green-100 border-4 border-green-400"
              : "bg-blue-50"
          }`}
        >
          <AnimatePresence mode="wait">
            <motion.img
              key={player.name}
              src={player.image}
              alt={player.name}
              className="w-40 h-40"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.4 }}
            />
          </AnimatePresence>
          <h2 className="font-bold text-xl mt-2 capitalize">{player.name}</h2>
          <div className="w-48 bg-gray-300 rounded-full h-4 mt-2">
            <motion.div
              className="bg-green-500 h-4 rounded-full"
              style={{ width: `${(player.hp / player.max_hp) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <p className="text-sm mt-1">
            Vida: {player.hp} / {player.max_hp}
          </p>
        </motion.div>

        {/* Enemigo */}
        <motion.div
          animate={shakeEnemy ? { x: [-8, 8, -8, 8, 0] } : {}}
          transition={{ duration: 0.3 }}
          className={`p-4 rounded-2xl shadow-lg flex flex-col items-center ${
            winner === "Enemigo"
              ? "bg-red-100 border-4 border-red-400"
              : "bg-red-50"
          }`}
        >
          <AnimatePresence mode="wait">
            <motion.img
              key={enemy.name}
              src={enemy.image}
              alt={enemy.name}
              className="w-40 h-40"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.5 }}
            />
          </AnimatePresence>
          <h2 className="font-bold text-xl mt-2 capitalize">{enemy.name}</h2>
          <div className="w-48 bg-gray-300 rounded-full h-4 mt-2">
            <motion.div
              className="bg-green-500 h-4 rounded-full"
              style={{ width: `${(enemy.hp / enemy.max_hp) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <p className="text-sm mt-1">
            Vida: {enemy.hp} / {enemy.max_hp}
          </p>
        </motion.div>
      </div>

      {/* 🎮 Controles */}
      {!winner ? (
        <div className="mt-6 flex gap-3">
          <button
            onClick={performRound}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
          >
            ⚔️ Atacar
          </button>
          <button
            onClick={heal}
            disabled={healsLeft <= 0}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition disabled:bg-gray-400"
          >
            🧪 Curar ({healsLeft})
          </button>
        </div>
      ) : (
        <div className="mt-6 text-center space-y-3">
          <h2
            className={`text-2xl font-bold ${
              winner === "Jugador" ? "text-green-700" : "text-red-700"
            }`}
          >
            🏆 {winner} ganó la batalla!
          </h2>

          {winner === "Jugador" && !captured && (
            <button
              onClick={capturePokemon}
              className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg transition"
            >
              🎯 Capturar Pokémon
            </button>
          )}

          <button
            onClick={getRandomPokemons}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
          >
            🔄 Nueva Batalla
          </button>

          <button
            onClick={() => navigate("/sorteos")}
            className="bg-gray-700 hover:bg-gray-800 text-white px-4 py-2 rounded-lg"
          >
            🔙 Regresar al Menú Principal
          </button>
        </div>
      )}

      {/* 📜 Registro */}
      <div className="bg-white shadow-md rounded-lg p-4 w-full max-w-2xl mt-6 h-56 overflow-y-auto border border-gray-200">
        <h3 className="font-semibold mb-2 text-lg">📜 Registro:</h3>
        <ul className="text-sm space-y-1">
          {log.map((line, i) => (
            <li key={i}>• {line}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
