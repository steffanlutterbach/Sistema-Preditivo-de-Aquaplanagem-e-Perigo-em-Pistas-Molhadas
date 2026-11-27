import { classeRisco, formatar, km, rotuloRisco } from "../../services/formatacao";

function Resultado({ consulta: c }) {
  if (c.status === "geometria_indisponivel") return <p className="nota">{c.observacao}</p>;
  if (!c.segmento_atual) {
    const perto = c.segmento_mais_proximo;
    return (
      <p className="nota">
        Fora da rodovia: o trecho mais próximo ({perto?.codigo ?? perto?.trecho_id}) está a {formatar(perto?.distancia_m, 0)} m.
      </p>
    );
  }
  const s = c.segmento_atual;
  return (
    <>
      <p>
        No trecho <b>{s.codigo}</b> (km {km(s.km_inicial)} a {km(s.km_final)}):{" "}
        <span className={`pilula ${classeRisco(s)}`}>{rotuloRisco(s)}</span>
      </p>
      {c.proximos_segmentos.length > 0 && (
        <>
          <h3>À frente, até {formatar(c.antecedencia_maxima_m / 1000, 0)} km</h3>
          <ul className="proximos">
            {c.proximos_segmentos.map((p) => (
              <li key={p.trecho_id}>
                <span>
                  {p.codigo} · em {formatar(p.distancia_ate_inicio_m / 1000)} km
                </span>
                <span className={`pilula ${classeRisco(p)}`}>{rotuloRisco(p)}</span>
              </li>
            ))}
          </ul>
        </>
      )}
      {c.alertas_relevantes.length > 0 ? (
        c.alertas_relevantes.map((a) => (
          <p className="alerta-motorista" key={a.chave_notificacao ?? a.id}>
            {a.mensagem}
          </p>
        ))
      ) : (
        <p className="nota">Nenhum alerta ativo à frente.</p>
      )}
      <p className="nota">
        Sentido {c.sentido_assumido ? "assumido" : "informado"}: {c.sentido_utilizado}. A localização não é armazenada.
      </p>
    </>
  );
}

export default function PainelMotorista({ consulta, erro, sentido, onSentido, posicao }) {
  return (
    <section className="painel motorista">
      <h2>Simular motorista</h2>
      <label className="campo">
        Sentido
        <select value={sentido} onChange={(e) => onSentido(e.target.value)}>
          <option value="">automático</option>
          <option value="crescente">km crescente</option>
          <option value="decrescente">km decrescente</option>
        </select>
      </label>
      {!posicao && <p className="nota">Clique no mapa, perto da rodovia, para ver o risco no trecho e à frente.</p>}
      {erro && <p className="aviso">{erro}</p>}
      {consulta && <Resultado consulta={consulta} />}
    </section>
  );
}
