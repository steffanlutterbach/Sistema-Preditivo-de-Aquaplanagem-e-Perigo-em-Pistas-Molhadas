"""Motor experimental do MVP; pontuações não são limiares de segurança."""

from datetime import datetime, timezone
from typing import Any

from app.repositories import registrar_analise, sincronizar_alerta
from app.services.calculo_vazao import calcular_lamina_agua, calcular_vazao, calcular_volume

VERSAO_ALGORITMO = "risk-v1-experimental"
FATOR_PAVIMENTO = {"bom": 0, "regular": 15, "ruim": 30, "irregular": 30}


def classificar_risco(pontuacao: float) -> str:
    if not 0 <= pontuacao <= 100:
        raise ValueError("A pontuação deve estar entre 0 e 100")
    if pontuacao < 35:
        return "baixo"
    if pontuacao < 70:
        return "moderado"
    return "alto"


def analisar_trecho(dados: dict[str, Any], persistir: bool = True) -> dict[str, Any]:
    """Registra uma análise rastreável e evita classificar dados insuficientes."""
    now = datetime.now(timezone.utc)
    measured_at = dados.get("data_hora") or now
    if isinstance(measured_at, str):
        measured_at = datetime.fromisoformat(measured_at.replace("Z", "+00:00"))
    if measured_at.tzinfo is None:
        measured_at = measured_at.replace(tzinfo=timezone.utc)
    age_seconds = max(0.0, (now - measured_at.astimezone(timezone.utc)).total_seconds())
    stale_after = float(dados.get("limite_atualidade_segundos", 3600))
    stale = age_seconds > stale_after

    intensity = dados.get("intensidade_mm_h")
    precipitation = dados.get("precipitacao_mm")
    pavement = (dados.get("estado_pavimento") or "").strip().lower()
    area = dados.get("area_contribuicao_m2")
    coefficient = dados.get("coeficiente_escoamento")
    drainage = dados.get("drenagem") or {}
    drainage_capacity = drainage.get("capacidade_total_l_s")
    missing = []
    if intensity is None:
        missing.append("intensidade_chuva")
    if precipitation is None:
        missing.append("precipitacao_acumulada")
    if not pavement or pavement not in FATOR_PAVIMENTO:
        missing.append("estado_pavimento")
    if area is None:
        missing.append("area_contribuicao_m2")
    if coefficient is None:
        missing.append("coeficiente_escoamento")
    if drainage_capacity is None:
        missing.append("capacidade_drenagem")
    origin = dados.get("origem_dados", "desconhecido")
    if origin not in {"mock", "real"}:
        missing.append("origem_dados")

    flow = None
    volume = None
    if intensity is not None and area is not None and coefficient is not None:
        flow = calcular_vazao(float(coefficient), float(intensity), float(area))
    if precipitation is not None and area is not None and coefficient is not None:
        volume = calcular_volume(float(precipitation), float(area), float(coefficient))
    drainage_adequate = None if flow is None or drainage_capacity is None else flow <= float(drainage_capacity)

    mtd = dados.get("mtd_mm")
    path_length = dados.get("caminho_escoamento_m")
    path_slope_pct = dados.get("declividade_caminho_percentual")
    wd_slope_source = (
        "declividade_caminho_percentual"
        if path_slope_pct is not None
        else None
    )
    wd = None
    wd_missing = [name for name, value in (("mtd_mm", mtd), ("caminho_escoamento_m", path_length),
                                          ("declividade_caminho_percentual", path_slope_pct),
                                          ("intensidade_mm_h", intensity)) if value is None]
    missing.extend(wd_missing)
    if not wd_missing:
        wd = calcular_lamina_agua(float(mtd), float(path_length), float(intensity), float(path_slope_pct))

    required_missing = {"intensidade_chuva", "precipitacao_acumulada", "estado_pavimento",
                        "area_contribuicao_m2", "coeficiente_escoamento", "capacidade_drenagem", "origem_dados"}
    score = None
    level = None
    status = "concluida"
    if stale:
        status = "dados_desatualizados"
        missing.append("medicao_desatualizada")
    elif required_missing.intersection(missing):
        status = "dados_insuficientes"
    else:
        score = min(100.0, float(intensity) * 2 + FATOR_PAVIMENTO[pavement])
        if drainage_adequate is False:
            score = min(100.0, score + 15.0)
        level = classificar_risco(score)

    analysis = {
        "trecho_id": dados["trecho_id"],
        "dados_clima_id": dados["dados_clima_id"],
        "vazao_estimada_l_s": round(flow, 3) if flow is not None else None,
        "volume_acumulado_l": round(volume, 3) if volume is not None else None,
        "pontuacao_risco": round(score, 2) if score is not None else None,
        "nivel_risco": level,
        "status_analise": status,
        "data_analise": now.isoformat(),
        "dados_utilizados": {
            "intensidade_mm_h": intensity,
            "precipitacao_mm": precipitation,
            "estado_pavimento": pavement or None,
            "inclinacao_percentual": dados.get("inclinacao_percentual"),
            "estado_inclinacao": dados.get("estado_inclinacao"),
            "area_contribuicao_m2": area,
            "coeficiente_escoamento": coefficient,
            "capacidade_drenagem_l_s": drainage_capacity,
            "drenagem_suficiente": drainage_adequate,
            "mtd_mm": mtd,
            "caminho_escoamento_m": path_length,
            "declividade_caminho_percentual": path_slope_pct,
            "wd_declividade_origem": wd_slope_source,
            "origem_dados": origin,
            "fonte_meteorologia": dados.get("fonte_meteorologia", "desconhecida"),
            "modo_meteorologia": dados.get("modo_meteorologia", "desconhecido"),
            "origem_trecho": dados.get("origem_trecho", "desconhecida"),
            "origem_geometria": dados.get("origem_geometria"),
            "geometria_validada": dados.get("geometria_validada", False),
            "medicao_data_hora": measured_at.isoformat(),
        },
        "versao_algoritmo": VERSAO_ALGORITMO,
        "origem_dados": origin,
        "dados_ausentes": sorted(set(missing)),
        "dados_desatualizados": stale,
        "classificacao_disponivel": level is not None,
        "classificacao_confiavel": False,
        "wd_mm": round(wd, 4) if wd is not None else None,
        "wd_status": "calculada_condicionalmente" if wd is not None else "indisponivel_parametros_ausentes",
        "wd_dados_ausentes": wd_missing,
        "observacao": "Classificação experimental para demonstração; não é previsão validada nem orientação de condução.",
    }
    if persistir:
        saved = registrar_analise(analysis)
        saved["alerta"] = sincronizar_alerta(saved)
    else:
        saved = {**analysis, "id": None, "alerta": None}
    return saved
