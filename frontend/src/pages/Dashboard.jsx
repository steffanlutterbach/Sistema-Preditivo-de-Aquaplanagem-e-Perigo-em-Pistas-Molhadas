import { useState } from "react";
import ErroApi from "../components/ErroApi/ErroApi";
import RiskCard from "../components/RiskCard/RiskCard";
import Sidebar from "../components/Sidebar/Sidebar";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatar, nomeTrecho } from "../services/formatacao";

function Indicador({ rotulo, valor, detalhe }) {
  return (
    <div className="indicador">
      <span>{rotulo}</span>
      <strong>{valor}</strong>
      <small>{detalhe}</small>
    </div>
  );
}

export default function Dashboard() {
  const mapa = useApi(api.mapaRiscos);
  const alertas = useApi(() => api.alertas(false));
  const cenarios = useApi(api.cenarios);
  const [selecionado, setSelecionado] = useState(null);
  const [cenario, setCenario] = useState("3");
  const [simulando, setSimulando] = useState(false);
  const [erroSimulacao, setErroSimulacao] = useState(null);
  const [versao, setVersao] = useState(0);

  if (mapa.erro) return <ErroApi mensagem={mapa.erro} />;
  if (!mapa.dados) return <p>Carregando…</p>;

  const trechos = mapa.dados.features.map((f) => f.properties);
  const atual = trechos.find((t) => t.id === selecionado) ?? trechos[0];
  const contar = (nivel) => trechos.filter((t) => t.nivel_risco === nivel).length;
  const semNivel = trechos.filter((t) => !t.nivel_risco).length;
  const maior = trechos.reduce((m, t) => ((t.pontuacao_risco ?? -1) > (m?.pontuacao_risco ?? -1) ? t : m), null);

  async function simular() {
    setSimulando(true);
    setErroSimulacao(null);
    try {
      for (const t of trechos) await api.simular(Number(cenario), t.id);
      mapa.recarregar();
      alertas.recarregar();
      setVersao((v) => v + 1);
    } catch (e) {
      setErroSimulacao(e.message);
    } finally {
      setSimulando(false);
    }
  }

  return (
    <>
      <h1>Risco de aquaplanagem por trecho</h1>
      <section className="painel simulacao">
        <label className="campo">
          Simular chuva
          <select value={cenario} onChange={(e) => setCenario(e.target.value)}>
            {(cenarios.dados?.cenarios ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.nome} · {formatar(c.intensidade_mm_h, 0)} mm/h
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="botao" onClick={simular} disabled={simulando || !cenarios.dados}>
          {simulando ? "Simulando…" : `Aplicar nos ${trechos.length} trechos`}
        </button>
        {erroSimulacao && <p className="aviso">{erroSimulacao}</p>}
        {semNivel === trechos.length && (
          <p className="nota">
            Ainda não há análises válidas. No modo mock, o backend começa vazio e cada análise vale por 60 minutos:
            escolha um cenário e clique em aplicar.
          </p>
        )}
      </section>
      <div className="indicadores">
        <Indicador
          rotulo="Trechos em risco alto"
          valor={`${contar("alto")} de ${trechos.length}`}
          detalhe={`${contar("moderado")} moderados · ${contar("baixo")} baixos · ${semNivel} sem nível`}
        />
        <Indicador
          rotulo="Maior pontuação"
          valor={formatar(maior?.pontuacao_risco, 2)}
          detalhe={maior?.pontuacao_risco != null ? nomeTrecho(maior) : "nenhuma análise ainda"}
        />
        <Indicador
          rotulo="Alertas ativos"
          valor={alertas.dados ? alertas.dados.length : "…"}
          detalhe="emitidos para risco moderado ou alto"
        />
      </div>
      <div className="grade">
        <Sidebar trechos={trechos} selecionado={atual?.id} onSelecionar={setSelecionado} />
        {atual && <RiskCard trecho={atual} versao={versao} />}
      </div>
    </>
  );
}
