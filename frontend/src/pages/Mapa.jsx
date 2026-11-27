import { useState } from "react";
import ErroApi from "../components/ErroApi/ErroApi";
import MapaRiscos from "../components/Map/MapaRiscos";
import PainelMotorista from "../components/Motorista/PainelMotorista";
import RiskCard from "../components/RiskCard/RiskCard";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

export default function Mapa() {
  const mapa = useApi(api.mapaRiscos);
  const [selecionado, setSelecionado] = useState(null);
  const [posicao, setPosicao] = useState(null);
  const [sentido, setSentido] = useState("");
  const [consulta, setConsulta] = useState(null);
  const [erroConsulta, setErroConsulta] = useState(null);

  if (mapa.erro) return <ErroApi mensagem={mapa.erro} />;
  if (!mapa.dados) return <p>Carregando…</p>;

  const trechos = mapa.dados.features.map((f) => f.properties);
  const atual = trechos.find((t) => t.id === selecionado) ?? trechos[0];

  async function consultarPosicao(latlng) {
    setPosicao(latlng);
    try {
      setConsulta(await api.localizacao(latlng.lat, latlng.lng, sentido || undefined));
      setErroConsulta(null);
    } catch (e) {
      setErroConsulta(e.message);
    }
  }

  return (
    <>
      <h1>Mapa de riscos</h1>
      <p className="nota">
        Geometria aproximada (dados de teste). Clique num trecho para ver a análise e em qualquer ponto do mapa para
        simular a posição de um motorista.
      </p>
      <div className="grade grade-mapa">
        <MapaRiscos
          geojson={mapa.dados}
          selecionado={atual?.id}
          onSelecionar={setSelecionado}
          posicao={posicao}
          onClique={consultarPosicao}
        />
        <div className="coluna">
          <PainelMotorista
            consulta={consulta}
            erro={erroConsulta}
            sentido={sentido}
            onSentido={setSentido}
            posicao={posicao}
          />
          {atual && <RiskCard trecho={atual} />}
        </div>
      </div>
    </>
  );
}
