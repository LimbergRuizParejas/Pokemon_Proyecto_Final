import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import BattleArena from "../components/BattleArena";
import { createBattle } from "../services/battle.js";

export default function Battle() {
  const [battleData, setBattleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const initializeBattle = async () => {
      try {
        setLoading(true);
        const battle = await createBattle();
        setBattleData(battle);
      } catch (err) {
        setError("Error al iniciar la batalla");
        console.error("Battle initialization error:", err);
      } finally {
        setLoading(false);
      }
    };

    initializeBattle();
  }, []);

  const updateBattleData = (newBattleData) => {
    setBattleData(newBattleData);
  };

  const handleBattleEnd = () => {
    navigate("/dashboard");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <Navbar />
        <div className="text-xl">Iniciando batalla...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <Navbar />
        <div className="text-xl text-red-500">{error}</div>
        <button 
          onClick={() => navigate("/mapa")}
          className="mt-4 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Volver al Mapa
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <Navbar />
      {battleData && (
        <BattleArena 
          battleData={battleData}
          updateBattleData={updateBattleData}
          onBattleEnd={handleBattleEnd}
        />
      )}
    </div>
  );
}