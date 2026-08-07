import { useEffect, useState } from "react";
import { getCars, getCategories, getMakes, getModels, search } from "./api";

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

const PAGE_SIZE = 12;

function flattenCategories(groups) {
  const items = [];
  for (const group of groups) {
    for (const pg of group.productgroups || []) {
      items.push({ id: pg.id, label: `${group.name} — ${pg.name} (${pg.count})` });
    }
  }
  return items;
}

export default function App() {
  const [makeId, setMakeId] = useState("");
  const [modelId, setModelId] = useState("");
  const [carId, setCarId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [page, setPage] = useState(1);

  const makes = useAsync(getMakes, []);
  const models = useAsync(() => getModels(makeId), [makeId], { skip: !makeId });
  const cars = useAsync(() => getCars(makeId, modelId), [makeId, modelId], { skip: !modelId });
  const categories = useAsync(() => getCategories(carId), [carId], { skip: !carId });
  const results = useAsync(
    () => search({ categoryId, carId, makeId, modelId }),
    [categoryId, carId, makeId, modelId],
    { skip: !categoryId },
  );

  const categoryOptions = flattenCategories(categories.data);

  useEffect(() => {
    setPage(1);
  }, [categoryId]);

  const totalPages = Math.max(1, Math.ceil(results.data.length / PAGE_SIZE));
  const pageItems = results.data.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="app-shell">
      <header className="topbar">
        <span className="brand">lojadoscoilovers</span>
        <span className="tagline">peças e suspensões pro seu carro</span>
      </header>

      <main>
        <fieldset className="filters">
          <legend>Encontre a peça certa pro seu veículo</legend>

          <div className="filters-grid">
            <label>
              Marca
              <select
                value={makeId}
                onChange={(e) => {
                  setMakeId(e.target.value);
                  setModelId("");
                  setCarId("");
                  setCategoryId("");
                }}
              >
                <option value="">Selecione a marca</option>
                {makes.data.map((make) => (
                  <option key={make.id} value={make.id}>
                    {make.name}
                  </option>
                ))}
              </select>
              {makes.loading && <span className="hint">carregando marcas...</span>}
              {makes.error && <span className="hint hint--error">erro: {makes.error}</span>}
            </label>

            <label>
              Modelo
              <select
                value={modelId}
                disabled={!makeId}
                onChange={(e) => {
                  setModelId(e.target.value);
                  setCarId("");
                  setCategoryId("");
                }}
              >
                <option value="">Selecione o modelo</option>
                {models.data.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
              {models.loading && <span className="hint">carregando modelos...</span>}
              {models.error && <span className="hint hint--error">erro: {models.error}</span>}
            </label>

            <label>
              Motorização
              <select
                value={carId}
                disabled={!modelId}
                onChange={(e) => {
                  setCarId(e.target.value);
                  setCategoryId("");
                }}
              >
                <option value="">Selecione a motorização</option>
                {cars.data.map((car) => (
                  <option key={car.id} value={car.id}>
                    {car.name}
                  </option>
                ))}
              </select>
              {cars.loading && <span className="hint">carregando motorizações...</span>}
              {cars.error && <span className="hint hint--error">erro: {cars.error}</span>}
            </label>

            <label>
              Categoria
              <select
                value={categoryId}
                disabled={!carId}
                onChange={(e) => setCategoryId(e.target.value)}
              >
                <option value="">Selecione a categoria</option>
                {categoryOptions.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
              {categories.loading && <span className="hint">carregando categorias...</span>}
              {categories.error && <span className="hint hint--error">erro: {categories.error}</span>}
            </label>
          </div>
        </fieldset>

        <section className="results">
          <h2>Resultados</h2>

          {!categoryId && (
            <p className="empty-state">Selecione marca, modelo, motorização e categoria pra ver produtos.</p>
          )}
          {results.loading && <p className="empty-state">Carregando resultados...</p>}
          {results.error && <p className="empty-state hint--error">Erro ao buscar: {results.error}</p>}
          {!results.loading && !results.error && categoryId && results.data.length === 0 && (
            <p className="empty-state">Nenhum produto encontrado pra esse veículo/categoria.</p>
          )}

          <ul className="results-grid">
            {pageItems.map((item) => (
              <li key={item.product_id} className="product-card">
                <div className="product-card__image">
                  {item.image ? <img src={item.image} alt={item.name} loading="lazy" /> : <span>sem imagem</span>}
                </div>
                <div className="product-card__body">
                  <strong>{item.name}</strong>
                  <span className="product-card__meta">
                    {item.brand} · {item.part_no}
                  </span>
                  <span className="product-card__price">
                    {item.price ? `€${item.price}` : "preço indisponível"}
                  </span>
                  {item.availability && (
                    <span
                      className="badge"
                      style={{ "--badge-color": item.availability.color || "#999" }}
                    >
                      {item.availability.text}
                    </span>
                  )}
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
              <button
                type="button"
                disabled={page === totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Próxima →
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
