import { classeRisco, formatar, km, rotuloRisco } from "../../services/formatacao";

export default function Sidebar({ trechos, selecionado, onSelecionar }) {
  return (
    <aside className="painel lista-trechos">
      <h2>Trechos</h2>
      <ul>
        {trechos.map((t) => (
          <li key={t.id}>
            <button type="button" className={t.id === selecionado ? "selecionado" : ""} onClick={() => onSelecionar(t.id)}>
              <span className="nome">
                <b>{t.codigo ?? `Trecho ${t.id}`}</b>
                <small>
                  km {km(t.km_inicial)} a {km(t.km_final)}
                </small>
              </span>
              <span className={`pilula ${classeRisco(t)}`}>{rotuloRisco(t)}</span>
              <b className="pontos">{formatar(t.pontuacao_risco)}</b>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
