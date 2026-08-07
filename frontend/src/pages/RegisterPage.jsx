import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../auth";

const EMPTY_FORM = {
  firstName: "",
  lastName: "",
  email: "",
  password: "",
  phone: "",
  deliveryAddress: "",
};

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  function update(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-form">
      <h2>Criar conta</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Nome
          <input value={form.firstName} onChange={update("firstName")} required />
        </label>
        <label>
          Sobrenome
          <input value={form.lastName} onChange={update("lastName")} />
        </label>
        <label>
          E-mail
          <input type="email" value={form.email} onChange={update("email")} required />
        </label>
        <label>
          Senha
          <input type="password" value={form.password} onChange={update("password")} required />
        </label>
        <label>
          Telefone
          <input value={form.phone} onChange={update("phone")} required />
        </label>
        <label>
          Endereço de entrega
          <textarea value={form.deliveryAddress} onChange={update("deliveryAddress")} required />
        </label>
        {error && <p className="hint hint--error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Criando conta..." : "Criar conta"}
        </button>
      </form>
      <p className="hint">
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </div>
  );
}
