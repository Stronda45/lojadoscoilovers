import { useEffect, useState } from "react";
import { catalogMakes, catalogModels, catalogSearch, catalogVariants } from "../api";

const PAGE_SIZE = 12;

function useAsync(loader, deps, { skip } = {}) {
  const [state, setState] = useState({ data: [], loading: false, error: null });

  useEffect(() => {
    if (skip) {
      setState({ data: [], loading: false, error: null });
      return;
    }
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    loader()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err) => {
        if (!cancelled) setState({ data: [], loading: false, error: err.message });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}

export default function CatalogPage() {
  const [q, setQ] = useState("");
  const [make, setMake] = useState("");
  const [model, setModel] = useState("");
  const [variant, setVariant] = useState("");
  const [page, setPage] = useState(1);

  const makes = useAsync(catalogMakes, []);
  const models = useAsync(() => catalogModels(make), [make], { skip: !make });
  const variants = useAsync(() => catalogVariants({ make, model }), [make, model], { skip: !make || !model });
  const results = useAsync(() => catalogSearch({ q, make, model, variant }), [q, make, model, variant]);

  useEffect(() => {
    setPage(1);
  }, [q, make, model, variant]);

  const totalPages = Math.max(1, Math.ceil(results.data.length / PAGE_SIZE));
  const pageItems = results.data.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const hasFilters = q || make || model || variant;

  function clearFilters() {
    setQ("");
    setMake("");
    setModel("");
    setVariant("");
  }

  return (
    <>
      <section className="hero" style={{ minHeight: "160px" }}>
        <div className="hero__content">
          <h1>Catálogo de outros fornecedores</h1>
          <p>Peças e rodas de fornecedores parceiros — pesquise por texto ou pelo seu veículo.</p>
        </div>
      </section>

      <fieldset className="filters">
        <legend>Pesquisar no catálogo</legend>
        {hasFilters && (
          <button type="button" className="clear-button" onClick={clearFilters}>
            Limpar pesquisa
          </button>
        )}

        <div className="filters-grid">
          <label>
            Texto
            <input
              type="text"
              placeholder="nome do produto..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </label>

          <label>
            Marca do veículo
            <select
              value={make}
              onChange={(e) => {
                setMake(e.target.value);
                setModel("");
                setVariant("");
              }}
            >
              <option value="">Todas as marcas</option>
              {makes.data.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            {makes.loading && <span className="hint">carregando marcas...</span>}
            {makes.error && <span className="hint hint--error">erro: {makes.error}</span>}
          </label>

          <label>
            Modelo
            <select
              value={model}
              disabled={!make}
              onChange={(e) => {
                setModel(e.target.value);
                setVariant("");
              }}
            >
              <option value="">Todos os modelos</option>
              {models.data.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            {models.loading && <span className="hint">carregando modelos...</span>}
          </label>

          <label>
            Motorização
            <select value={variant} disabled={!model} onChange={(e) => setVariant(e.target.value)}>
              <option value="">Todas</option>
              {variants.data.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
            {variants.loading && <span className="hint">carregando motorizações...</span>}
          </label>
        </div>
      </fieldset>

      <section className="results">
        <h2>Resultados</h2>

        <p className="notice">
          Estes produtos não são pedidos direto pelo site — entre em contacto para confirmar
          disponibilidade e finalizar a compra.
        </p>

        {results.loading && <p className="empty-state">Carregando resultados...</p>}
        {results.error && <p className="empty-state hint--error">Erro ao buscar: {results.error}</p>}
        {!results.loading && !results.error && results.data.length === 0 && (
          <p className="empty-state">Nenhum produto encontrado.</p>
        )}

        <ul className="results-grid">
          {pageItems.map((item) => (
            <li key={item.id} className="product-card">
              <div className="product-card__image">
                {item.image_url ? (
                  <img src={item.image_url} alt={item.title} loading="lazy" />
                ) : (
                  <span>sem imagem</span>
                )}
              </div>
              <div className="product-card__body">
                <strong>{item.title}</strong>
                <span className="product-card__meta">
                  {item.supplier} · {item.external_reference}
                </span>
                <span className="product-card__price">
                  {item.price ? `€${item.price}` : "preço sob consulta"}
                </span>
              </div>
            </li>
          ))}
        </ul>

        {results.data.length > PAGE_SIZE && (
          <div className="pagination">
            <button type="button" disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
              ← Anterior
            </button>
            <span>
              Página {page} de {totalPages}
            </span>
            <button type="button" disabled={page === totalPages} onClick={() => setPage((p) => p + 1)}>
              Próxima →
            </button>
          </div>
        )}
      </section>
    </>
  );
}
