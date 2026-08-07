const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function extractErrorMessage(body, fallback) {
  if (!body || typeof body !== "object") return fallback;
  if (body.detail) return body.detail;
  // Erros de validação do DRF vem como {"campo": ["mensagem", ...], ...}
  const messages = Object.values(body).flat().filter((v) => typeof v === "string");
  return messages.length ? messages.join(" ") : fallback;
}

async function request(method, path, { params, body, token } = {}) {
  const url = new URL(path, API_BASE_URL);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, value);
      }
    });
  }

  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Token ${token}`;

  const response = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) return null;

  const responseBody = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(extractErrorMessage(responseBody, `Erro ${response.status} ao consultar ${path}`));
  }
  return responseBody;
}

const apiGet = (path, params) => request("GET", path, { params });
const apiPost = (path, body, token) => request("POST", path, { body, token });

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

export function register({ email, password, firstName, lastName, phone, deliveryAddress }) {
  return apiPost("/auth/register", {
    email,
    password,
    first_name: firstName,
    last_name: lastName,
    phone,
    delivery_address: deliveryAddress,
  });
}

export function login({ email, password }) {
  return apiPost("/auth/login", { email, password });
}

export function logout(token) {
  return apiPost("/auth/logout", undefined, token);
}

export function createOrder(items, token) {
  return apiPost("/orders", { items }, token);
}

export function listOrders(token) {
  return request("GET", "/orders", { token });
}
