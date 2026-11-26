"""Matching temporário de posição com segmentos; coordenadas não são retidas."""

from math import asin, cos, radians, sin, sqrt
from typing import Any

from app.core.config import ALERT_LEAD_DISTANCE_METERS, DATA_MODE, LOCATION_MATCH_TOLERANCE_METERS
from app.repositories import dados_desatualizados, listar_alertas, listar_analises, listar_trechos

EARTH_RADIUS_M = 6_371_000


def _haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(radians, a)
    lat2, lon2 = map(radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(h))


def _segment_distance(point: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    """Distância local aproximada e fração projetada ao longo do segmento."""
    lat0 = radians(point[0])
    scale_x = cos(lat0) * radians(1) * EARTH_RADIUS_M
    scale_y = radians(1) * EARTH_RADIUS_M
    ax, ay = (a[1] - point[1]) * scale_x, (a[0] - point[0]) * scale_y
    bx, by = (b[1] - point[1]) * scale_x, (b[0] - point[0]) * scale_y
    dx, dy = bx - ax, by - ay
    denominator = dx * dx + dy * dy
    fraction = 0.0 if denominator == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / denominator))
    return sqrt((ax + fraction * dx) ** 2 + (ay + fraction * dy) ** 2), fraction


def _geometry_points(segment: dict[str, Any]) -> list[tuple[float, float]]:
    geometry = segment.get("geometria")
    if geometry and geometry.get("type") == "LineString":
        return [(float(lat), float(lon)) for lon, lat, *_ in geometry["coordinates"]]
    endpoints = segment.get("coordenadas_aproximadas") or {}
    start, end = endpoints.get("inicio"), endpoints.get("fim")
    if start and end:
        return [(float(start["latitude"]), float(start["longitude"])),
                (float(end["latitude"]), float(end["longitude"]))]
    return []


def consultar_riscos_proximos(latitude: float, longitude: float, sentido: str | None) -> dict[str, Any]:
    point = (latitude, longitude)
    segments = listar_trechos()
    candidates = []
    for segment in segments:
        if DATA_MODE == "real" and not segment.get("geometria_validada"):
            continue
        points = _geometry_points(segment)
        if len(points) < 2:
            continue
        nearest, fraction = min((_segment_distance(point, a, b) for a, b in zip(points, points[1:])), key=lambda result: result[0])
        candidates.append((nearest, fraction, segment, points))

    mode_note = "geometria_mock_aproximada; correspondência apenas para teste" if DATA_MODE == "mock" else "geometria_validada"
    if not candidates:
        return {"status": "geometria_indisponivel", "localizacao_processada": True,
                "localizacao_armazenada": False, "segmento_atual": None, "proximos_segmentos": [],
                "alertas_relevantes": [], "observacao": "Não há geometrias elegíveis para este ambiente."}

    nearest, fraction, current, points = min(candidates, key=lambda item: item[0])
    matched = nearest <= LOCATION_MATCH_TOLERANCE_METERS
    direction = sentido or "crescente"
    ordered = sorted(segments, key=lambda item: float(item.get("km_inicial", 0)), reverse=direction == "decrescente")
    current_index = next((i for i, item in enumerate(ordered) if item["id"] == current["id"]), 0)
    remaining = (1 - fraction) * float(current.get("comprimento_m", _haversine(points[0], points[-1]))) if direction == "crescente" else fraction * float(current.get("comprimento_m", _haversine(points[0], points[-1])))
    start_distance = max(0.0, remaining)
    upcoming = []
    cursor_distance = start_distance
    for item in ordered[current_index + 1:]:
        if cursor_distance > ALERT_LEAD_DISTANCE_METERS:
            break
        length = float(item.get("comprimento_m", 0))
        upcoming.append({"trecho": item, "distancia_ate_inicio_m": round(cursor_distance, 1)})
        cursor_distance += length

    current_risk = next((a for a in listar_alertas(trecho_id=int(current["id"])) if a.get("status") == "ativo"), None) if matched else None
    current_analyses = listar_analises(int(current["id"])) if matched else []
    current_analysis = current_analyses[0] if current_analyses else None
    if current_analysis and dados_desatualizados(current_analysis.get("data_analise")):
        current_analysis = {**current_analysis, "nivel_risco": None, "status_analise": "dados_desatualizados",
                            "dados_desatualizados": True}
    relevant = []
    if current_risk:
        relevant.append({**current_risk, "distancia_ate_trecho_m": 0.0,
                         "chave_notificacao": current_risk.get("chave_notificacao", f"alerta:{current_risk['id']}")})
    next_segments = []
    for entry in upcoming:
        segment = entry["trecho"]
        risk = next((a for a in listar_alertas(trecho_id=int(segment["id"])) if a.get("status") == "ativo"), None)
        analyses = listar_analises(int(segment["id"]))
        latest = analyses[0] if analyses else None
        if latest and dados_desatualizados(latest.get("data_analise")):
            latest = {**latest, "nivel_risco": None, "status_analise": "dados_desatualizados",
                      "dados_desatualizados": True}
        next_segments.append({"trecho_id": segment["id"], "codigo": segment.get("codigo"),
                              "km_inicial": segment.get("km_inicial"), "km_final": segment.get("km_final"),
                              "distancia_ate_inicio_m": entry["distancia_ate_inicio_m"],
                              "nivel_risco": latest.get("nivel_risco") if latest else None,
                              "status_analise": latest.get("status_analise", "sem_analises") if latest else "sem_analises",
                              "data_ultima_analise": latest.get("data_analise") if latest else None,
                              "dados_desatualizados": latest.get("dados_desatualizados", False) if latest else False,
                              "origem_dados": latest.get("origem_dados") if latest else None,
                              "alerta": risk, "geometria_validada": segment.get("geometria_validada", False)})
        if risk:
            relevant.append({**risk, "distancia_ate_trecho_m": entry["distancia_ate_inicio_m"],
                             "chave_notificacao": risk.get("chave_notificacao", f"alerta:{risk['id']}")})

    return {
        "status": "correspondencia_encontrada" if matched else "fora_da_tolerancia",
        "localizacao_processada": True,
        "localizacao_armazenada": False,
        "segmento_atual": {"trecho_id": current["id"], "codigo": current.get("codigo"),
                           "km_inicial": current.get("km_inicial"), "km_final": current.get("km_final"),
                           "nivel_risco": current_analysis.get("nivel_risco") if current_analysis else None,
                           "status_analise": current_analysis.get("status_analise", "sem_analises") if current_analysis else "sem_analises",
                           "data_ultima_analise": current_analysis.get("data_analise") if current_analysis else None,
                           "distancia_ate_segmento_m": round(nearest, 1)} if matched else None,
        "segmento_mais_proximo": None if matched else {"trecho_id": current["id"], "codigo": current.get("codigo"),
                                                        "distancia_m": round(nearest, 1)},
        "distancia_ate_segmento_m": round(nearest, 1),
        "proximos_segmentos": next_segments if matched else [],
        "alertas_relevantes": relevant if matched else [],
        "sentido_utilizado": direction,
        "sentido_assumido": sentido is None,
        "antecedencia_maxima_m": ALERT_LEAD_DISTANCE_METERS,
        "validade_e_chave_alerta_incluidas": True,
        "origem_geometria": mode_note,
        "observacao": "Distâncias ao longo da rota usam comprimentos cadastrados; geometria mock aproximada não deve ser usada para navegação real." if DATA_MODE == "mock" else "Distâncias ao longo da rota usam comprimentos cadastrados.",
    }
