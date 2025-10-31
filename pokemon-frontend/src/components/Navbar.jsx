import { useState, useContext } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import { AuthContext } from "../context/AuthContext.jsx";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);

  const links = [
    { to: "/", label: "Ciudad" },
    { to: "/capture", label: "Captura" },
    { to: "/battle", label: "Batalla" },
    { to: "/dashboard", label: "Dashboard" },
    { to: "/reportes", label: "Reportes" },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="fixed top-0 left-0 w-full z-50 backdrop-blur-md bg-white/70 border-b border-blue-100 shadow-sm py-2">
      <div className="max-w-7xl mx-auto px-6 sm:px-10">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <img src={logo} alt="PokeAPI Logo" className="h-24 w-auto" />
          </div>

          <div className="hidden md:flex items-center space-x-6">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`font-medium transition-colors ${
                  location.pathname === link.to
                    ? "text-blue-700 font-semibold border-b-2 border-yellow-400"
                    : "text-gray-600 hover:text-blue-600"
                }`}
              >
                {link.label}
              </Link>
            ))}

            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-gray-700 font-medium">
                  👋 Hola,{" "}
                  <span className="text-blue-700 font-semibold capitalize">
                    {user.username}
                  </span>
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white font-semibold px-3 py-1.5 rounded-lg text-sm transition"
                >
                  Cerrar sesión
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition"
              >
                Iniciar sesión
              </Link>
            )}
          </div>

          <button
            onClick={() => setOpen(!open)}
            className="md:hidden text-blue-700 focus:outline-none text-2xl"
          >
            {open ? "✖" : "☰"}
          </button>
        </div>
      </div>

      {open && (
        <div className="md:hidden bg-white/95 shadow-md border-t border-blue-100 text-center py-3 space-y-2">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={() => setOpen(false)}
              className={`block py-2 text-lg font-medium ${
                location.pathname === link.to
                  ? "text-blue-700 font-semibold"
                  : "text-gray-700 hover:text-blue-600"
              }`}
            >
              {link.label}
            </Link>
          ))}

          {user ? (
            <>
              <p className="text-gray-700 font-medium mt-2">
                👋 Hola,{" "}
                <span className="text-blue-700 font-semibold capitalize">
                  {user.username}
                </span>
              </p>
              <button
                onClick={() => {
                  setOpen(false);
                  handleLogout();
                }}
                className="mt-2 bg-red-500 hover:bg-red-600 text-white font-semibold px-4 py-2 rounded-lg text-sm transition"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <Link
              to="/login"
              onClick={() => setOpen(false)}
              className="block bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg mt-3"
            >
              Iniciar sesión
            </Link>
          )}
        </div>
      )}
    </nav>
  );
}
