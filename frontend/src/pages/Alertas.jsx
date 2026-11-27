import { useState } from "react";
import ErroApi from "../components/ErroApi/ErroApi";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { dataHora, hora, nomeTrecho } from "../services/formatacao";

// O front mostra só os alertas ativos e o histórico. Os status "resolvido" e
// "expirado" são controle interno do backend; no histórico aparecem como "encerrado".
const ABAS = [
  ["ativos", "Ativos"],
  ["historico", "Histórico"],
];

export default function Alertas() {
  const [aba, setAba] = useState("ativos");
  const historico = aba === "historico";
  const alertas = useApi(() => api.alertas(historico), [historico]);
  const trechos = useApi(api.trechos);

  const porId = Object.fromEntries((trechos.dados ?? []).map((t) => [t.id, t]));
  const lista = (alertas.dados ?? [])
    .filter((a) => historico || a.status === "ativo")
    .sort((a, b) => String(b.data_hora).localeCompare(String(a.data_hora)));

  return (
    <>
      <h1>Alertas</h1>
      <div className="filtros">
        {ABAS.map(([valor, rotulo]) => (
          <button key={valor} type="button" className={aba === valor ? "ativa" : ""} onClick={() => setAba(valor)}>
            {rotulo}
          </button>
        ))}
      </div>
      {alertas.erro && <ErroApi mensagem={alertas.erro} />}
      {alertas.carregando && !alertas.dados && <p>Carregando…</p>}
      {alertas.dados && lista.length === 0 && (
        <p className="vazio">
          {historico ? "Nenhum alerta registrado ainda." : "Nenhum alerta ativo no momento."} Rode uma simulação no
          Dashboard para gerar alertas.
        </p>
      )}
      <div className="lista-alertas">
        {lista.map((a) => {
          const trecho = porId[a.trecho_id];
          const ativo = a.status === "ativo";
          return (
            <article className="painel alerta" key={a.id}>
              <header>
                <h2>
                  Alerta #{a.id} · {trecho ? nomeTrecho(trecho) : `Trecho ${a.trecho_id}`}
                </h2>
                <span className={`pilula status-${ativo ? "ativo" : "encerrado"}`}>{ativo ? "ativo" : "encerrado"}</span>
              </header>
              <p>
                <span className={`pilula ${a.nivel}`}>{a.nivel}</span> {a.mensagem}
              </p>
              <small>
                Emitido em {dataHora(a.data_hora)} · válido até {hora(a.validade)} · análise #{a.analise_id}
              </small>
            </article>
          );
        })}
      </div>
    </>
  );
}
