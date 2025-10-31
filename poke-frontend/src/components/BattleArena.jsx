import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { 
  attackInBattle, 
  healInBattle, 
  captureInBattle, 
  fleeFromBattle,
  changePokemonInBattle 
} from "../services/battle.js";

export default function BattleArena({ battleData, updateBattleData }) {
  const navigate = useNavigate();
  
  const [log, setLog] = useState("Cargando batalla...");
  const [showMoves, setShowMoves] = useState(false);
  const [showBag, setShowBag] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessingTurn, setIsProcessingTurn] = useState(false);

  useEffect(() => {
    if (battleData && battleData.pokemon_salvaje) {
      setLog(`¡Un ${battleData.pokemon_salvaje.name} salvaje apareció!`);
    }
  }, [battleData]);

  const handleBattleEnd = () => {
    navigate("/dashboard");
  };

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const showMessageWithDelay = async (message, delayTime = 1500) => {
    setLog(message);
    await delay(delayTime);
  };

  const updateBattleState = (response) => {
    const updatedBattle = { ...battleData };
    
    if (response.accion === "atacar") {
      updatedBattle.hp_salvaje_actual = response.hp_salvaje_restante;
      updatedBattle.user_pokemon_actual.current_hp = response.hp_usuario_actual;
      
      if (response.nuevo_pokemon_actual) {
        const newPokemon = updatedBattle.equipo_usuario.find(
          p => p.user_pokemon_id === response.nuevo_pokemon_actual
        );
        if (newPokemon) {
          updatedBattle.user_pokemon_actual = newPokemon;
        }
      }
    } else if (response.accion === "capturar") {
      updatedBattle.pokebolas_restantes = response.pokebolas_restantes;
      updatedBattle.user_pokemon_actual.current_hp = response.hp_actual_usuario;
    } else if (response.accion === "curar") {
      updatedBattle.curaciones_restantes = response.curaciones_restantes;
      updatedBattle.user_pokemon_actual.current_hp = response.hp_actual_usuario;
    } else if (response.accion === "huir") {
    }
    
    updatedBattle.estado = response.batalla_terminada ? "terminada" : "activa";
    
    updateBattleData(updatedBattle);
    
    return response.batalla_terminada;
  };

  const switchToNextPokemon = async () => {
    if (!battleData) return false;

    const team = battleData.equipo_usuario;
    const currentPokemonId = battleData.user_pokemon_actual.user_pokemon_id;
    
    for (let i = 0; i < team.length; i++) {
      const nextPokemon = team[i];
      
      if (nextPokemon.current_hp > 0 && nextPokemon.user_pokemon_id !== currentPokemonId) {
        try {
          const response = await changePokemonInBattle(battleData.id, nextPokemon.user_pokemon_id);
          await showMessageWithDelay(`¡Ve! ${nextPokemon.pokemon.name}!`);
          updateBattleState(response);
          return true;
        } catch (error) {
          await showMessageWithDelay("Error al cambiar de Pokémon");
          console.error(error);
          return false;
        }
      }
    }
    
    await showMessageWithDelay("¡No tienes más Pokémon que usar!");
    return false;
  };

  const handleAttack = async (move) => {
    if (!battleData || !battleData.user_pokemon_actual || isLoading || isProcessingTurn) return;

    setShowMoves(false);
    setIsLoading(true);
    setIsProcessingTurn(true);
    
    try {
      await showMessageWithDelay(`${battleData.user_pokemon_actual.pokemon.name} usó ${move.name}!`);
      
      const response = await attackInBattle(
        battleData.id, 
        battleData.user_pokemon_actual.user_pokemon_id, 
        move.id
      );

      if (response.error) {
        await showMessageWithDelay(response.error);
        handleBattleEnd();
        return;
      }

      if (response.resultado_usuario) {
        let effectivenessMessage = "";
        if (response.resultado_usuario.multiplicador_efectividad > 1) {
          effectivenessMessage = "¡Es super efectivo!";
        } else if (response.resultado_usuario.multiplicador_efectividad < 1) {
          effectivenessMessage = "No es muy efectivo...";
        } else {
          effectivenessMessage = "Efectividad normal.";
        }
        
        await showMessageWithDelay(
          `${effectivenessMessage} ¡Infligió ${response.resultado_usuario.danio} puntos de daño!`
        );
      }

      const battleEnded = updateBattleState(response);

      if (battleEnded && response.resultado_batalla === "ganada") {
        await showMessageWithDelay(response.mensaje, 2000);
        handleBattleEnd();
        return;
      }

      if (response.hp_salvaje_restante <= 0) {
        await showMessageWithDelay("¡El Pokémon enemigo fue derrotado!", 2000);
        return;
      }

      if (response.resultado_salvaje) {
        await showMessageWithDelay(
          `¡${battleData.pokemon_salvaje.name} usó ${response.resultado_salvaje.movimiento}!`
        );

        let enemyEffectivenessMessage = "";
        if (response.resultado_salvaje.multiplicador_efectividad > 1) {
          enemyEffectivenessMessage = "¡Es super efectivo!";
        } else if (response.resultado_salvaje.multiplicador_efectividad < 1) {
          enemyEffectivenessMessage = "No es muy efectivo...";
        } else {
          enemyEffectivenessMessage = "Efectividad normal.";
        }

        await showMessageWithDelay(
          `${enemyEffectivenessMessage} ¡Infligió ${response.resultado_salvaje.danio} puntos de daño!`
        );

        if (response.hp_usuario_actual <= 0) {
          await showMessageWithDelay(`¡${battleData.user_pokemon_actual.pokemon.name} fue derrotado!`);
          
          const hasNextPokemon = await switchToNextPokemon();
          if (!hasNextPokemon) {
            await showMessageWithDelay("¡Has perdido la batalla!", 2000);
            handleBattleEnd();
          }
        }
      }

    } catch (error) {
      if (error.message && error.message.includes("terminado")) {
        await showMessageWithDelay(error.message);
        handleBattleEnd();
      } else {
        await showMessageWithDelay("Error al ejecutar el ataque");
        console.error(error);
      }
    } finally {
      setIsLoading(false);
      setIsProcessingTurn(false);
    }
  };

  const handleHeal = async () => {
    if (!battleData || !battleData.user_pokemon_actual || battleData.curaciones_restantes <= 0 || isLoading || isProcessingTurn) return;

    setShowBag(false);
    setIsLoading(true);
    setIsProcessingTurn(true);
    
    try {
      await showMessageWithDelay("Usaste una cura.");
      
      const response = await healInBattle(battleData.id, battleData.user_pokemon_actual.user_pokemon_id);

      if (response.error) {
        await showMessageWithDelay(response.error);
        handleBattleEnd();
        return;
      }

      await showMessageWithDelay(
        `¡${battleData.user_pokemon_actual.pokemon.name} recuperó ${response.curacion_aplicada} puntos de salud!`
      );

      updateBattleState(response);

      if (response.resultado_salvaje && response.resultado_salvaje.danio > 0) {
        await showMessageWithDelay(
          `¡${battleData.pokemon_salvaje.name} usó ${response.resultado_salvaje.movimiento}!`
        );

        await showMessageWithDelay(
          `¡Infligió ${response.resultado_salvaje.danio} puntos de daño!`
        );
      } else if (response.resultado_salvaje) {
        await showMessageWithDelay(
          `¡${battleData.pokemon_salvaje.name} usó ${response.resultado_salvaje.movimiento}!`
        );
        await showMessageWithDelay("No tuvo efecto...");
      }

    } catch (error) {
      if (error.message && error.message.includes("terminado")) {
        await showMessageWithDelay(error.message);
        handleBattleEnd();
      } else {
        await showMessageWithDelay("Error al usar la cura");
        console.error(error);
      }
    } finally {
      setIsLoading(false);
      setIsProcessingTurn(false);
    }
  };

  const handleCapture = async () => {
    if (!battleData || !battleData.user_pokemon_actual || battleData.pokebolas_restantes <= 0 || isLoading || isProcessingTurn) return;

    setShowBag(false);
    setIsLoading(true);
    setIsProcessingTurn(true);
    
    try {
      await showMessageWithDelay(`Lanzaste una Pokéball a ${battleData.pokemon_salvaje.name}!`);
      
      const response = await captureInBattle(battleData.id, battleData.user_pokemon_actual.user_pokemon_id);

      if (response.error) {
        await showMessageWithDelay(response.error);
        handleBattleEnd();
        return;
      }

      await showMessageWithDelay(response.mensaje);

      if (response.resultado === "éxito") {
        await showMessageWithDelay("¡Felicidades! ¡Pokémon atrapado!", 2000);
        updateBattleState(response);
        handleBattleEnd();
        return;
      }

      updateBattleState(response);

      if (response.resultado_salvaje) {
        await showMessageWithDelay(
          `¡${battleData.pokemon_salvaje.name} usó ${response.resultado_salvaje.movimiento}!`
        );

        await showMessageWithDelay(
          `¡Infligió ${response.resultado_salvaje.danio} puntos de daño!`
        );
      }

    } catch (error) {
      if (error.message && error.message.includes("terminado")) {
        await showMessageWithDelay(error.message);
        handleBattleEnd();
      } else {
        await showMessageWithDelay("Error al usar la Pokéball");
        console.error(error);
      }
    } finally {
      setIsLoading(false);
      setIsProcessingTurn(false);
    }
  };

  const handleFlee = async () => {
    if (!battleData || isLoading || isProcessingTurn) return;

    setIsLoading(true);
    setIsProcessingTurn(true);
    
    try {
      const response = await fleeFromBattle(battleData.id);
      
      if (response.error) {
        await showMessageWithDelay(response.error);
        handleBattleEnd();
        return;
      }

      await showMessageWithDelay(response.mensaje);
      updateBattleState(response);
      
      if (response.batalla_terminada) {
        await delay(2000);
        handleBattleEnd();
      }

    } catch (error) {
      if (error.message && error.message.includes("terminado")) {
        await showMessageWithDelay(error.message);
        handleBattleEnd();
      } else {
        await showMessageWithDelay("No puedes huir en este momento");
        console.error(error);
      }
    } finally {
      setIsLoading(false);
      setIsProcessingTurn(false);
    }
  };

  const handleSwitchPokemon = async () => {
    if (!battleData || isLoading || isProcessingTurn) return;
    
    const hasSwitched = await switchToNextPokemon();
    if (!hasSwitched) {
      setLog("No hay otros Pokémon disponibles");
    }
  };

  if (!battleData || !battleData.pokemon_salvaje || !battleData.user_pokemon_actual) {
    return (
      <div className="relative w-[880px] h-[500px] border-4 border-blue-300 rounded-xl shadow-lg mt-24 flex items-center justify-center">
        <div className="text-xl">Cargando batalla...</div>
      </div>
    );
  }

  const enemy = {
    name: battleData.pokemon_salvaje.name,
    frontSprite: battleData.pokemon_salvaje.sprites.front_default,
    maxHP: battleData.pokemon_salvaje.stats.hp,
  };

  const player = {
    name: battleData.user_pokemon_actual.pokemon.name,
    backSprite: battleData.user_pokemon_actual.pokemon.sprites.back_default,
    maxHP: battleData.user_pokemon_actual.pokemon.stats.hp,
  };

  const enemyHPPercent = (battleData.hp_salvaje_actual / enemy.maxHP) * 100;
  const playerHPPercent = (battleData.user_pokemon_actual.current_hp / player.maxHP) * 100;

  const isBattleActive = battleData.estado === "activa";
  const isActionDisabled = isLoading || isProcessingTurn || !isBattleActive;

  return (
    <div
      className="relative w-[880px] h-[500px] border-4 border-blue-300 rounded-xl shadow-lg mt-24 overflow-hidden"
      style={{
        backgroundImage: "url('/src/assets/fondo-batalla.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* 📊 Cuadro de vida del enemigo */}
      <div className="absolute top-10 left-25 bg-white/95 border border-gray-400 px-4 py-2 rounded-lg shadow w-80">
        <h2 className="text-lg font-bold text-gray-700 capitalize">{enemy.name}</h2>
        <div className="w-full bg-gray-200 h-3 rounded mt-1">
          <div
            className={`h-3 rounded transition-all duration-500 ${
              enemyHPPercent > 50 ? "bg-green-500" : enemyHPPercent > 20 ? "bg-yellow-500" : "bg-red-500"
            }`}
            style={{ width: `${enemyHPPercent}%` }}
          ></div>
        </div>
        <span className="text-sm text-gray-600">
          {battleData.hp_salvaje_actual} / {enemy.maxHP}
        </span>
      </div>

      {/* 🧊 Sprite enemigo */}
      <motion.img
        src={enemy.frontSprite}
        alt={enemy.name}
        className="absolute top-2 right-30 h-72 drop-shadow-lg"
        animate={{ y: [0, -6, 0] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      />

      {/* 🌿 Sprite jugador */}
      <motion.img
        src={player.backSprite}
        alt={player.name}
        className="absolute bottom-15 left-20 h-80 drop-shadow-lg"
        animate={{ y: [0, 6, 0] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      />

      {/* 📊 Cuadro de vida jugador */}
      <div className="absolute bottom-40 right-30 bg-white/95 border border-gray-400 px-4 py-2 rounded-lg shadow w-80">
        <h2 className="text-lg font-bold text-gray-700 capitalize">{player.name}</h2>
        <div className="w-full bg-gray-200 h-3 rounded mt-1">
          <div
            className={`h-3 rounded transition-all duration-500 ${
              playerHPPercent > 50 ? "bg-green-500" : playerHPPercent > 20 ? "bg-yellow-500" : "bg-red-500"
            }`}
            style={{ width: `${playerHPPercent}%` }}
          ></div>
        </div>
        <span className="text-sm text-gray-600">
          {battleData.user_pokemon_actual.current_hp} / {player.maxHP}
        </span>
      </div>

      {/* 🕹️ Cuadro de comandos */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-white/95 border border-gray-400 rounded-lg shadow-lg w-[820px] h-[120px] grid grid-cols-2 gap-4 p-4">
        {/* Texto del log */}
        <div className="flex items-center justify-center border border-gray-300 rounded p-3 text-gray-800 font-medium">
          {log}
        </div>

        {/* Botones o movimientos */}
        {showMoves ? (
          <div className="grid grid-cols-2 gap-2">
            {battleData.user_pokemon_actual.pokemon.movimientos.map((move) => (
              <button
                key={move.id}
                onClick={() => handleAttack(move)}
                disabled={isActionDisabled}
                className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-2 rounded capitalize transition-colors"
              >
                {move.name.replace('-', ' ')}
              </button>
            ))}
          </div>
        ) : showBag ? (
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleHeal}
              disabled={isActionDisabled || battleData.curaciones_restantes <= 0}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Cura ({battleData.curaciones_restantes})
            </button>
            <button
              onClick={handleCapture}
              disabled={isActionDisabled || battleData.pokebolas_restantes <= 0}
              className="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Pokéball ({battleData.pokebolas_restantes})
            </button>
            <button
              onClick={() => setShowBag(false)}
              disabled={isActionDisabled}
              className="bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Volver
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setShowMoves(true)}
              disabled={isActionDisabled}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Luchar
            </button>
            <button
              onClick={() => setShowBag(true)}
              disabled={isActionDisabled}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Mochila
            </button>
            <button
              onClick={handleSwitchPokemon}
              disabled={isActionDisabled || battleData.equipo_usuario.length <= 1}
              className="bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-400 text-blue-900 font-bold py-2 px-4 rounded transition-colors"
            >
              Pokémon
            </button>
            <button
              onClick={handleFlee}
              disabled={isActionDisabled}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Huir
            </button>
          </div>
        )}
      </div>

      {/* Indicador de estado de batalla */}
      {!isBattleActive && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg text-center">
            <h3 className="text-xl font-bold mb-4">Batalla Terminada</h3>
            <p className="mb-4">{log}</p>
            <button 
              onClick={handleBattleEnd}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
            >
              Volver al Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}