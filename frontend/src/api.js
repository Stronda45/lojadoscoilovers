const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function apiGet(path, params = {}) {
  const url = new URL(path, API_BASE_URL);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Erro ${response.status} ao consultar ${path}`);
  }
  return response.json();
}

export function getMakes() {
  return apiGet("/vehicles/makes");
}

export function getModels(makeId) {
  return apiGet(`/vehicles/makes/${makeId}/models`);
}

export function getCars(makeId, modelId) {
  return apiGet("/vehicles/cars", { make_id: makeId, model_id: modelId });
}

export function getCategories(carId) {
  return apiGet(`/vehicles/${carId}/categories`);
}

export function search({ categoryId, carId, makeId, modelId }) {
  return apiGet("/search", {
    category_id: categoryId,
    car_id: carId,
    make_id: makeId,
    model_id: modelId,
  });
}
