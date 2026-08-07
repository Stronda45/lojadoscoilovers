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

  return (
    <main>
      <h1>Buscar peça</h1>

      <fieldset>
        <legend>Veículo</legend>

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
          {makes.loading && <span> carregando marcas...</span>}
          {makes.error && <span role="alert"> erro: {makes.error}</span>}
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
          {models.loading && <span> carregando modelos...</span>}
          {models.error && <span role="alert"> erro: {models.error}</span>}
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
          {cars.loading && <span> carregando motorizações...</span>}
          {cars.error && <span role="alert"> erro: {cars.error}</span>}
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
          {categories.loading && <span> carregando categorias...</span>}
          {categories.error && <span role="alert"> erro: {categories.error}</span>}
        </label>
      </fieldset>

      <section>
        <h2>Resultados</h2>

        {!categoryId && <p>Selecione marca, modelo, motorização e categoria pra ver produtos.</p>}
        {results.loading && <p>Carregando resultados...</p>}
        {results.error && <p role="alert">Erro ao buscar: {results.error}</p>}
        {!results.loading && !results.error && categoryId && results.data.length === 0 && (
          <p>Nenhum produto encontrado.</p>
        )}

        <ul>
          {results.data.map((item) => (
            <li key={item.product_id}>
              {item.image && <img src={item.image} alt={item.name} width={80} />}
              <div>
                <strong>{item.name}</strong> — {item.brand} ({item.part_no})
                <br />
                {item.price ? `€${item.price}` : "preço indisponível"}
                {item.availability && <> — {item.availability.text}</>}
              </div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
