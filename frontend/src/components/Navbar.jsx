import { Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar({ currentPage, onNavigate }) {
  const { isAuthenticated, user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    onNavigate("home");
  };

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 flex justify-between h-16 items-center">

        <div
          className="flex items-center space-x-2 cursor-pointer"
          onClick={() => onNavigate("home")}
        >
          <Sparkles className="w-6 h-6 text-purple-600" />
          <span className="text-xl font-bold">EduSphere</span>
        </div>

        <div className="flex items-center space-x-6">
          <button onClick={() => onNavigate("home")}>Home</button>
          <button onClick={() => onNavigate("dashboard")}>Dashboard</button>
          <button onClick={() => onNavigate("about")}>About</button>

          {isAuthenticated ? (
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="text-sm bg-gray-100 hover:bg-gray-200 rounded-lg px-3 py-1.5"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-3">
              <button onClick={() => onNavigate("login")}>Log in</button>
              <button
                onClick={() => onNavigate("register")}
                className="bg-purple-600 text-white rounded-lg px-3 py-1.5 text-sm hover:bg-purple-700"
              >
                Sign up
              </button>
            </div>
          )}
        </div>

      </div>
    </nav>
  );
}
