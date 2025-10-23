import { Routes, Route, Navigate } from "react-router-dom";

// 🧩 Páginas activas
import City from "../pages/City.jsx";
import Capture from "../pages/Capture.jsx";
import Battle from "../pages/Battle.jsx";
import Login from "../pages/Login.jsx";
import Register from "../pages/Register.jsx";

// 🔒 Rutas protegidas
import PrivateRoute from "../components/PrivateRoute.jsx";

/**
 * Configuración principal del enrutador
 * -------------------------------------
 * Rutas públicas (login, registro, ciudad)
 * y rutas privadas (batalla, captura).
 * Incluye manejo de 404 y redirección desde /sorteos.
 */
export default function RouterConfig() {
  return (
    <Routes>
      {/* 🏙️ Rutas públicas */}
      <Route path="/" element={<City />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* ⚔️ Rutas protegidas */}
      <Route
        path="/capture"
        element={
          <PrivateRoute>
            <Capture />
          </PrivateRoute>
        }
      />
      <Route
        path="/battle"
        element={
          <PrivateRoute>
            <Battle />
          </PrivateRoute>
        }
      />

      {/* 🎯 Solución al botón “Regresar al menú principal” */}
      <Route path="/sorteos" element={<Navigate to="/" replace />} />

      {/* 🚫 Página 404 (rutas inexistentes) */}
      <Route
        path="*"
        element={
          <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
            <h1 className="text-4xl font-bold text-red-600 mb-4">
              404 - Página no encontrada
            </h1>
            <p className="text-gray-700 mb-6">
              La ruta que intentas acceder no existe.
            </p>
            <a
              href="/"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              Volver al inicio
            </a>
          </div>
        }
      />
    </Routes>
  );
}
