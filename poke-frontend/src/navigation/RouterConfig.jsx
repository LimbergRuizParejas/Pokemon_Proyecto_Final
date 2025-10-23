import { Routes, Route } from "react-router-dom";
import City from "../pages/City.jsx";
import Capture from "../pages/Capture.jsx";
import Battle from "../pages/Battle.jsx";
import Dashboard from "../pages/Dashboard.jsx";
import Reportes from "../pages/Reportes.jsx";
import Login from "../pages/Login.jsx";
import Register from "../pages/Register.jsx";
import PrivateRoute from "../components/PrivateRoute.jsx";

export default function RouterConfig() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<City />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Rutas protegidas */}
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
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/reportes"
        element={
          <PrivateRoute>
            <Reportes />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
