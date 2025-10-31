import { Routes, Route } from "react-router-dom";
import Login from "../pages/Login.jsx";
import Register from "../pages/Register.jsx";
import SelectStarter from "../pages/SelectStarter.jsx";
import Battle from "../pages/Battle.jsx";
import PrivateRoute from "../components/PrivateRoute.jsx";

export default function RouterConfig() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/select-starter"
        element={
          <PrivateRoute>
            <SelectStarter />
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

      {/* Redirección por defecto */}
      <Route path="*" element={<Login />} />
    </Routes>
  );
}
