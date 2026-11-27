import { CircleMarker, GeoJSON, MapContainer, TileLayer, useMapEvents } from "react-leaflet";
import { km, rotuloRisco } from "../../services/formatacao";

const CORES = { baixo: "#22C55E", moderado: "#FACC15", alto: "#EF4444" };

function limites(geojson) {
  const pontos = geojson.features.flatMap((f) => f.geometry?.coordinates ?? []);
  const lats = pontos.map((c) => c[1]);
  const lons = pontos.map((c) => c[0]);
  return [
    [Math.min(...lats), Math.min(...lons)],
    [Math.max(...lats), Math.max(...lons)],
  ];
}

function CliqueNoMapa({ onClique }) {
  useMapEvents({ click: (evento) => onClique?.(evento.latlng) });
  return null;
}

export default function MapaRiscos({ geojson, selecionado, onSelecionar, posicao, onClique }) {
  const estilo = (feature) => {
    const p = feature.properties;
    return {
      color: CORES[p.nivel_risco] ?? "#94A3B8",
      weight: p.id === selecionado ? 12 : 7,
      opacity: 0.95,
      dashArray: p.nivel_risco ? null : "6 6",
    };
  };

  const aoCriarCamada = (feature, camada) => {
    const p = feature.properties;
    camada.bindTooltip(`${p.codigo ?? `Trecho ${p.id}`} · km ${km(p.km_inicial)} a ${km(p.km_final)}: ${rotuloRisco(p)}`, {
      sticky: true,
    });
    camada.on("click", () => onSelecionar(p.id));
  };

  // A chave muda com os dados e a seleção, para o Leaflet redesenhar as linhas.
  const chave = `${selecionado}-${geojson.features.map((f) => `${f.properties.nivel_risco}${f.properties.pontuacao_risco}`).join(",")}`;

  return (
    <MapContainer bounds={limites(geojson)} boundsOptions={{ padding: [32, 32] }} scrollWheelZoom className="mapa">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON key={chave} data={geojson} style={estilo} onEachFeature={aoCriarCamada} />
      {posicao && (
        <CircleMarker
          center={[posicao.lat, posicao.lng]}
          radius={8}
          pathOptions={{ color: "#F4F8FB", fillColor: "#38BDF8", fillOpacity: 0.95, weight: 2 }}
        />
      )}
      <CliqueNoMapa onClique={onClique} />
    </MapContainer>
  );
}
