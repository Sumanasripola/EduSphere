import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import About from "./pages/About";
import Login from "./pages/Login";
import Register from "./pages/Register";

function AppContent() {
  const [currentPage, setCurrentPage] = useState("home");
  const { isAuthenticated, loading } = useAuth();

  const navigate = (page) => {
    // Gate the dashboard behind login. Check localStorage directly (not the
    // isAuthenticated state variable) because localStorage is written
    // synchronously inside login()/register(), while React state updates
    // land one render later — checking state here could still see the
    // "logged out" value for one extra click right after logging in.
    const hasToken = !!localStorage.getItem("access_token");
    if (page === "dashboard" && !hasToken) {
      setCurrentPage("login");
      return;
    }
    setCurrentPage(page);
  };

  const renderPage = () => {
    if (loading) {
      return <div className="min-h-[70vh] flex items-center justify-center">Loading...</div>;
    }

    if (currentPage === "dashboard") {
      return isAuthenticated ? <Dashboard /> : <Login onNavigate={navigate} />;
    }

    if (currentPage === "login") {
      return <Login onNavigate={navigate} />;
    }

    if (currentPage === "register") {
      return <Register onNavigate={navigate} />;
    }

    if (currentPage === "about") {
      return (
        <>
          <About />
          <Footer />
        </>
      );
    }

    return (
      <>
        <Home onNavigate={navigate} />
        <Footer />
      </>
    );
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar currentPage={currentPage} onNavigate={navigate} />
      <main className="flex-1">{renderPage()}</main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
