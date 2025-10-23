import Navbar from "../components/Navbar";
export default function Dashboard() {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-yellow-100">
       <Navbar />
      <h1 className="text-4xl font-extrabold text-blue-700">
        Página de Dashboard 📊
      </h1>
    </div>
  );
}
