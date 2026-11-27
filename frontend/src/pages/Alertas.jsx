import { useState } from "react";
import ErroApi from "../components/ErroApi/ErroApi";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { hora, nomeTrecho } from "../services/formatacao";

const FILTROS = [
  ["ativo", "Ativos"],
  ["todos", "Histórico completo"],
  ["resolvido", "Resolvidos"],
  ["expirado", "Expirados"],
];

export default function Alertas() {
  const [filtro, setFiltro] = useState("ativo");
  const alertas = useApi(() => api.alertas(filtro !== "ativo"), [filtro]);
  const trechos = useApi(api.trechos);

  const porId = Object.fromEntries((trechos.dados ?? []).map((t) => [t.id, t]));
  const lista = (alertas.dados ?? [])
    .filter((a) => filtro === "ativo" || filtro === "todos" || a.status === filtro)
    .sort((a, b) => String(b.data_hora).localeCompare(String(a.data_hora)));

  return (
    <>
      <h1>Alertas</h1>
      <div className="filtros">
        {FILTROS.map(([valor, rotulo]) => (
          <button key={valor} type="button" className={filtro === valor ? "ativa" : ""} onClick={() => setFiltro(valor)}>
            {rotulo}
          </button>
        ))}
      </div>
      {alertas.erro && <ErroApi mensagem={alertas.erro} />}
      {alertas.carregando && !alertas.dados && <p>Carregando…</p>}
      {alertas.dados && lista.length === 0 && (
        <p className="vazio">Nenhum alerta com este filtro. Rode uma simulação no Dashboard para gerar alertas.</p>
      )}
      <div className="lista-alertas">
        {lista.map((a) => {
          const trecho = porId[a.trecho_id];
          return (
            <article className="painel alerta" key={a.id}>
              <header>
                <h2>
                  Alerta #{a.id} · {trecho ? nomeTrecho(trecho) : `Trecho ${a.trecho_id}`}
                </h2>
                <span className={`pilula status-${a.status}`}>{a.status}</span>
              </header>
              <p>
                <span className={`pilula ${a.nivel}`}>{a.nivel}</span> {a.mensagem}
              </p>
              <small>
                Emitido às {hora(a.data_hora)} · válido até {hora(a.validade)} · análise #{a.analise_id}
              </small>
            </article>
          );
        })}
      </div>
    </>
  );
}
