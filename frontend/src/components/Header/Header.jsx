import { useApi } from "../../hooks/useApi";
import { api } from "../../services/api";

const ABAS = [
  ["dashboard", "Dashboard"],
  ["mapa", "Mapa"],
  ["alertas", "Alertas"],
];

export default function Header({ pagina, onNavegar }) {
  const { dados: saude, erro } = useApi(api.saude);
  const selo = erro ? "API fora do ar" : saude ? `DATA_MODE=${saude.modo_dados}` : "conectando…";
  return (
    <header className="topo">
      <div className="marca">
        <span className="gota" aria-hidden="true" />
        <div>
          <strong>AquaSafe</strong>
          <small>Monitoramento de risco de aquaplanagem</small>
        </div>
      </div>
      <nav className="abas" aria-label="Páginas">
        {ABAS.map(([id, rotulo]) => (
          <button
            key={id}
            type="button"
            className={pagina === id ? "ativa" : ""}
            aria-current={pagina === id ? "page" : undefined}
            onClick={() => onNavegar(id)}
          >
            {rotulo}
          </button>
        ))}
      </nav>
      <span className={`selo${erro ? " selo-erro" : ""}`}>{selo}</span>
    </header>
  );
}
