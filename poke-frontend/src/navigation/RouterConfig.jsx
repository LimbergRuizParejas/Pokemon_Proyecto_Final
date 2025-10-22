import { Routes, Route } from "react-router-dom";
import City from "../pages/City.jsx";
import Capture from "../pages/Capture.jsx";
import Login from "../pages/Login.jsx";
import Register from "../pages/Register.jsx";

export default function RouterConfig() {
  return (
    <Routes>
      <Route path="/" element={<City />} />
      <Route path="/capture" element={<Capture />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}
