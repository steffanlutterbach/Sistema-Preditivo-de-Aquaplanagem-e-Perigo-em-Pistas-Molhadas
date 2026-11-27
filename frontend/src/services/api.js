const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

function cabecalhos(extras = {}) {
  return API_KEY ? { ...extras, "X-API-Key": API_KEY } : extras;
}

async function tratarResposta(response, path) {
  if (!response.ok) {
    let detalhe = "";
    try {
      const corpo = await response.json();
      detalhe = typeof corpo.detail === "string" ? corpo.detail : JSON.stringify(corpo.detail);
    } catch {
      // resposta sem corpo JSON
    }
    throw new Error(`Erro ${response.status} ao acessar ${path}${detalhe ? `: ${detalhe}` : ""}`);
  }
  return response.json();
}

export async function getJson(path) {
  const response = await fetch(`${API_URL}${path}`, { headers: cabecalhos() });
  return tratarResposta(response, path);
}

export async function postJson(path, body) {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: cabecalhos({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  return tratarResposta(response, path);
}

export const api = {
  saude: () => getJson("/health"),
  trechos: () => getJson("/trechos"),
  risco: (trechoId) => getJson(`/trechos/${trechoId}/risco`),
  mapaRiscos: () => getJson("/mapa/riscos"),
  alertas: (historico = false) => getJson(historico ? "/alertas?historico=true" : "/alertas"),
  cenarios: () => getJson("/simulacoes/cenarios"),
  simular: (cenarioId, trechoId) => postJson("/simulacoes", { cenario_id: cenarioId, trecho_id: trechoId }),
  localizacao: (latitude, longitude, sentido) =>
    postJson("/monitoramento/localizacao", sentido ? { latitude, longitude, sentido } : { latitude, longitude }),
};
