import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function AccountPage() {
  const { auth, deleteAccount } = useAuth();
  const navigate = useNavigate();
  const [confirming, setConfirming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!auth) {
    return <p className="empty-state">Faça login pra ver sua conta.</p>;
  }

  async function handleDelete() {
    setLoading(true);
    setError(null);
    try {
      await deleteAccount();
      navigate("/");
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="auth-form">
      <h2>Minha conta</h2>
      <p className="hint">E-mail: {auth.email}</p>

      <div className="danger-zone">
        <h3>Excluir minha conta</h3>
        <p className="hint">
          Seus dados pessoais (nome, e-mail, telefone, endereço) são removidos.
          Pedidos já feitos continuam registrados (histórico de compra), sem dados
          que identifiquem você. Essa ação não pode ser desfeita.
        </p>

        {!confirming ? (
          <button type="button" className="danger-button" onClick={() => setConfirming(true)}>
            Excluir minha conta
          </button>
        ) : (
          <>
            <p className="hint hint--error">Tem certeza? Não dá pra desfazer.</p>
            <button type="button" className="danger-button" disabled={loading} onClick={handleDelete}>
              {loading ? "Excluindo..." : "Sim, excluir de vez"}
            </button>
            <button type="button" onClick={() => setConfirming(false)} disabled={loading}>
              Cancelar
            </button>
          </>
        )}
        {error && <p className="hint hint--error">{error}</p>}
      </div>
    </div>
  );
}
