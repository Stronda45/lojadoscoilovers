import { BrowserRouter, Link, Route, Routes, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import LoginPage from "./pages/LoginPage";
import OrdersPage from "./pages/OrdersPage";
import RegisterPage from "./pages/RegisterPage";
import SearchPage from "./pages/SearchPage";

function Nav() {
  const { auth, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <nav className="nav">
      {auth ? (
        <>
          <span className="nav__email">{auth.email}</span>
          <Link to="/pedidos">Meus pedidos</Link>
          <button type="button" onClick={handleLogout}>
            Sair
          </button>
        </>
      ) : (
        <>
          <Link to="/login">Entrar</Link>
          <Link to="/cadastro">Cadastrar</Link>
        </>
      )}
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app-shell">
          <header className="topbar">
            <Link to="/" className="brand-link">
              <span className="brand">lojadoscoilovers</span>
              <span className="tagline">peças e suspensões pro seu carro</span>
            </Link>
            <Nav />
          </header>

          <main>
            <Routes>
              <Route path="/" element={<SearchPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/cadastro" element={<RegisterPage />} />
              <Route path="/pedidos" element={<OrdersPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
