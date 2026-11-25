const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getJson(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Erro ${response.status} ao acessar ${path}`);
  }
  return response.json();
}
