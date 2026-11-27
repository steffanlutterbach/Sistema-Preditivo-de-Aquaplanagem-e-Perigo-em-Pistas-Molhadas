import { useApi } from "../../hooks/useApi";
import { api } from "../../services/api";
import { classeRisco, formatar, hora, nomeTrecho, rotuloRisco } from "../../services/formatacao";

function Numero({ rotulo, children }) {
  return (
    <div>
      <dt>{rotulo}</dt>
      <dd>{children}</dd>
    </div>
  );
}

export default function RiskCard({ trecho, versao = 0 }) {
  const { dados: r, erro, carregando } = useApi(() => api.risco(trecho.id), [trecho.id, versao]);
  if (erro) return <section className="painel erro">{erro}</section>;
  if (!r) return <section className="painel">{carregando ? "Carregando…" : "Sem dados."}</section>;

  if (r.status_analise === "sem_analises") {
    return (
      <section className="painel cartao-risco">
        <header>
          <div>
            <small>{nomeTrecho(trecho)}</small>
            <h2>Sem análise</h2>
          </div>
          <span className="pilula sem-dado">sem análise</span>
        </header>
        <p className="nota">Ainda não há análise para este trecho. Use “Simular chuva” no Dashboard para gerar uma.</p>
      </section>
    );
  }

  const d = r.dados_utilizados ?? {};
  const drenagem =
    d.drenagem_suficiente === false ? " · não dá conta" : d.drenagem_suficiente ? " · dá conta" : "";
  return (
    <section className="painel cartao-risco">
      <header>
        <div>
          <small>
            {nomeTrecho(trecho)} · análise das {hora(r.data_analise)}
          </small>
          <h2>{r.pontuacao_risco == null ? "Sem pontuação" : `${formatar(r.pontuacao_risco, 2)} pontos`}</h2>
        </div>
        <span className={`pilula ${classeRisco(r)}`}>{rotuloRisco(r)}</span>
      </header>
      <dl className="numeros">
        <Numero rotulo="Chuva">{formatar(d.intensidade_mm_h)} mm/h</Numero>
        <Numero rotulo="Precipitação acumulada">{formatar(d.precipitacao_mm)} mm</Numero>
        <Numero rotulo="Vazão estimada (Q)">{formatar(r.vazao_estimada_l_s)} L/s</Numero>
        <Numero rotulo="Capacidade da drenagem">
          {formatar(d.capacidade_drenagem_l_s, 0)} L/s{drenagem}
        </Numero>
        <Numero rotulo="Volume acumulado (V)">
          {r.volume_acumulado_l == null ? "—" : `${formatar(r.volume_acumulado_l / 1000)} m³`}
        </Numero>
        <Numero rotulo="Lâmina d'água (WD)">{r.wd_mm == null ? "não calculada" : `${formatar(r.wd_mm, 2)} mm`}</Numero>
      </dl>
      {r.dados_ausentes?.length > 0 && <p className="aviso">Dados ausentes: {r.dados_ausentes.join(", ")}.</p>}
      <p className="nota">
        {r.versao_algoritmo} · origem {r.origem_dados}. {r.observacao}
      </p>
    </section>
  );
}
