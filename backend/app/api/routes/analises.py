"""Execução e histórico das análises de risco."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.config import DATA_MODE
from app.repositories import (
    consultar_trecho, listar_analises, listar_medicoes, obter_medicao_recente,
    registrar_medicao,
)
from app.schemas import AnaliseRiscoInput
from app.services.classificacao_risco import analisar_trecho

router = APIRouter(prefix="/analises", tags=["analises"])


@router.post("")
def executar_analise(dados: AnaliseRiscoInput):
    trecho = consultar_trecho(dados.trecho_id)
    if trecho is None:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")

    weather = obter_medicao_recente(dados.trecho_id)
    if dados.intensidade_mm_h is not None or dados.precipitacao_mm is not None:
        stamp = dados.data_hora or datetime.now(timezone.utc)
        source = "MOCK_ANALISE" if DATA_MODE == "mock" else "API_ANALISE"
        same = next((m for m in listar_medicoes(dados.trecho_id)
                     if m.get("fonte") == source and m.get("data_hora") == stamp.isoformat()), None)
        if same:
            if same.get("intensidade_mm_h") != dados.intensidade_mm_h or same.get("precipitacao_mm") != dados.precipitacao_mm:
                raise HTTPException(status_code=409, detail="Já existe medição com esta fonte e data/hora, mas valores diferentes")
            weather = same
        else:
            try:
                weather = registrar_medicao({
                    "trecho_id": dados.trecho_id,
                    "fonte": source,
                    "precipitacao_mm": dados.precipitacao_mm,
                    "intensidade_mm_h": dados.intensidade_mm_h,
                    "data_hora": stamp,
                    "modo_dados": "mock" if DATA_MODE == "mock" else "real",
                })
            except ValueError as erro:
                raise HTTPException(status_code=409, detail=str(erro)) from erro

    if weather is None:
        raise HTTPException(status_code=422, detail="Não há medição meteorológica para o trecho; registre uma medição ou informe precipitação/intensidade")

    intensity = dados.intensidade_mm_h if dados.intensidade_mm_h is not None else weather.get("intensidade_mm_h")
    precipitation = dados.precipitacao_mm if dados.precipitacao_mm is not None else weather.get("precipitacao_mm")
    stamp = dados.data_hora or weather.get("data_hora")
    if isinstance(stamp, str):
        stamp = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    drainage = trecho.get("drenagem") or {}
    analysis_input = {
        "trecho_id": dados.trecho_id,
        "dados_clima_id": weather["id"],
        "intensidade_mm_h": intensity,
        "precipitacao_mm": precipitation,
        "estado_pavimento": dados.estado_pavimento or trecho.get("estado_pavimento"),
        "inclinacao_percentual": trecho.get("inclinacao_percentual"),
        "estado_inclinacao": trecho.get("estado_inclinacao"),
        "data_hora": stamp,
        "area_contribuicao_m2": trecho.get("area_contribuicao_m2"),
        "coeficiente_escoamento": trecho.get("coeficiente_escoamento"),
        "drenagem": drainage,
        "mtd_mm": trecho.get("mtd_mm"),
        "caminho_escoamento_m": trecho.get("caminho_escoamento_m"),
        "declividade_caminho_percentual": trecho.get("declividade_caminho_percentual"),
        "origem_dados": weather.get("modo_dados", "mock" if DATA_MODE == "mock" else "real"),
    }
    try:
        return analisar_trecho(analysis_input)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@router.get("")
def consultar_analises(trecho_id: int | None = None):
    if trecho_id is not None and consultar_trecho(trecho_id) is None:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return listar_analises(trecho_id)
