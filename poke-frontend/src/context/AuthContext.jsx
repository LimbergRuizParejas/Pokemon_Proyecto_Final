import { createContext, useState, useEffect } from "react";
import {jwtDecode}  from "jwt-decode";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser({
          username: decoded.username || decoded.user || "Entrenador",
          token,
        });
      } catch (err) {
        console.error("Error al decodificar token:", err);
        localStorage.removeItem("token");
      }
    }
  }, []);

  const login = (token) => {
    try {
      const decoded = jwtDecode(token);
      setUser({
        username: decoded.username || decoded.user || "Entrenador",
        token,
      });
      localStorage.setItem("token", token);
    } catch (err) {
      console.error("Error al decodificar token:", err);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
