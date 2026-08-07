import { createContext, useContext, useEffect, useState } from "react";
import { login as apiLogin, logout as apiLogout, register as apiRegister } from "./api";

const STORAGE_KEY = "loja_auth";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  });

  useEffect(() => {
    if (auth) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [auth]);

  async function login(email, password) {
    const { token } = await apiLogin({ email, password });
    setAuth({ token, email });
  }

  async function register(payload) {
    const { token } = await apiRegister(payload);
    setAuth({ token, email: payload.email });
  }

  async function logout() {
    if (auth) {
      await apiLogout(auth.token).catch(() => {});
    }
    setAuth(null);
  }

  return (
    <AuthContext.Provider value={{ auth, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro de <AuthProvider>");
  return ctx;
}
