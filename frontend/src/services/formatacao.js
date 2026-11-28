const STATUS = {
  sem_analises: "sem análise",
  dados_insuficientes: "dados insuficientes",
  dados_desatualizados: "desatualizado",
  concluida: "concluída",
};

export function formatar(valor, casas = 1) {
  if (valor == null || Number.isNaN(Number(valor))) return "—";
  return Number(valor).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
}

export function km(valor) {
  return valor == null ? "—" : Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 1 });
}

/** Hora local (HH:MM) de uma data ISO; o backend guarda em UTC. */
export function hora(iso) {
  if (!iso) return "—";
  const data = new Date(iso);
  return Number.isNaN(data.getTime()) ? "—" : data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

/** Nível de risco ou, quando não há nível, o motivo (sem análise, dados insuficientes...). */
export function rotuloRisco(item) {
  return item?.nivel_risco ?? STATUS[item?.status_analise] ?? "sem análise";
}

export function classeRisco(item) {
  return item?.nivel_risco ?? "sem-dado";
}

export function nomeTrecho(trecho) {
  return `${trecho.codigo ?? `Trecho ${trecho.id}`} · km ${km(trecho.km_inicial)} a ${km(trecho.km_final)}`;
}
