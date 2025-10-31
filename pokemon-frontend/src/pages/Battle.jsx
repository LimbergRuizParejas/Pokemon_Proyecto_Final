import Navbar from "../components/Navbar";
import BattleArena from "../components/BattleArena";

export default function Battle() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <Navbar />
      <BattleArena />
    </div>
  );
}
