import { useEffect, useState } from "react";
import { listOrders } from "../api";
import { useAuth } from "../auth";

const STATUS_LABELS = {
  pending: "Pendente",
  ordered_with_supplier: "Comprado no fornecedor",
  delivered: "Entregue",
};

export default function OrdersPage() {
  const { auth } = useAuth();
  const [state, setState] = useState({ data: [], loading: true, error: null });

  useEffect(() => {
    if (!auth) return;
    listOrders(auth.token)
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err) => setState({ data: [], loading: false, error: err.message }));
  }, [auth]);

  if (!auth) {
    return <p className="empty-state">Faça login pra ver seus pedidos.</p>;
  }

  return (
    <section className="results">
      <h2>Meus pedidos</h2>

      {state.loading && <p className="empty-state">Carregando pedidos...</p>}
      {state.error && <p className="empty-state hint--error">Erro ao buscar: {state.error}</p>}
      {!state.loading && !state.error && state.data.length === 0 && (
        <p className="empty-state">Nenhum pedido ainda.</p>
      )}

      <ul className="orders-list">
        {state.data.map((order) => (
          <li key={order.id} className="order-card">
            <div className="order-card__header">
              <strong>Pedido #{order.id}</strong>
              <span className="badge" style={{ "--badge-color": "#1f3a93" }}>
                {STATUS_LABELS[order.status] || order.status}
              </span>
            </div>
            <ul>
              {order.items.map((item) => (
                <li key={item.id}>
                  {item.product_name} × {item.quantity} — €{item.sale_price}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </section>
  );
}
