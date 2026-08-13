import { BrowserRouter, Link, Route, Routes, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import AccountPage from "./pages/AccountPage";
import CatalogPage from "./pages/CatalogPage";
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
          <Link to="/conta">Minha conta</Link>
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
              <img src="/logo.jpg" alt="Loja dos Coilovers" className="brand-logo" />
              <span className="brand">Loja dos Coilovers</span>
              <span className="tagline">peças e suspensões pro seu carro</span>
            </Link>
            <Link to="/catalogo" className="nav__catalog-link">
              Outros fornecedores
            </Link>
            <Nav />
          </header>

          <main>
            <Routes>
              <Route path="/" element={<SearchPage />} />
              <Route path="/catalogo" element={<CatalogPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/cadastro" element={<RegisterPage />} />
              <Route path="/pedidos" element={<OrdersPage />} />
              <Route path="/conta" element={<AccountPage />} />
            </Routes>
          </main>

          <footer className="site-footer">
            <span>
              Site criado por{" "}
              <a
                href="https://wa.me/351911509368?text=Ol%C3%A1%20Pablo%2C%20vi%20seu%20contacto%20no%20rodap%C3%A9%20de%20um%20site%20e%20gostaria%20de%20falar%20sobre%20um%20projeto%20freelancer."
                target="_blank"
                rel="noopener noreferrer"
              >
                Pablo ©
              </a>{" "}
              — disponível para trabalhos freelancer
            </span>
          </footer>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
