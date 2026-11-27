"""Ponto de entrada da API AquaSafe."""

import hmac

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alertas, analises, meteorologia, monitoramento, rodovias, trechos
from app.core.config import API_KEY, CORS_ORIGINS, DATA_MODE
from app.repositories import (
    dados_desatualizados, listar_analises, listar_cenarios,
    listar_rodovias, listar_trechos, listar_medicoes,
    registrar_medicao, verificar_banco,
)
from app.schemas import SimulacaoInput
from app.services.classificacao_risco import analisar_trecho


def exigir_api_key(x_api_key: str | None = Header(default=None)):
    if API_KEY and (x_api_key is None or not hmac.compare_digest(x_api_key, API_KEY)):
        raise HTTPException(status_code=401, detail="Credencial de API inválida ou ausente")


app = FastAPI(
    title="AquaSafe",
    description="API experimental de monitoramento de risco de aquaplanagem",
    version="0.2.0",
    dependencies=[Depends(exigir_api_key)],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "PUT"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(rodovias.router)
app.include_router(trechos.router)
app.include_router(meteorologia.router)
app.include_router(analises.router)
app.include_router(alertas.router)
app.include_router(monitoramento.router)


@app.exception_handler(psycopg.Error)
async def falha_banco_handler(_request, _erro):
    return JSONResponse(status_code=503, content={"detail": "Banco de dados indisponível ou migration pendente."})


@app.get("/mapa/riscos")
def mapa_riscos():
    roads_by_id = {item["id"]: item for item in listar_rodovias()}
    features = []
    for segment in listar_trechos():
        analyses = listar_analises(int(segment["id"]))
        latest = analyses[0] if analyses else {}
        stale = dados_desatualizados(latest.get("data_analise")) if latest else False
        level = None if stale else latest.get("nivel_risco")
        properties = {key: value for key, value in segment.items() if key != "geometria"}
        properties.update({
            "rodovia": roads_by_id.get(segment["rodovia_id"]),
            "nivel_risco": level,
            "status_analise": "dados_desatualizados" if stale else latest.get("status_analise", "sem_analises"),
            "pontuacao_risco": latest.get("pontuacao_risco"),
            "data_analise": latest.get("data_analise"),
            "origem_dados": latest.get("origem_dados", segment.get("origem_dados", "mock")),
            "dados_desatualizados": stale or latest.get("dados_desatualizados", False),
        })
        features.append({"type": "Feature", "geometry": segment.get("geometria"), "properties": properties})
    return {"type": "FeatureCollection", "features": features}


@app.get("/simulacoes/cenarios")
def consultar_cenarios():
    return {"modo_dados": "mock", "cenarios": listar_cenarios()}


@app.post("/simulacoes")
def executar_simulacao(dados: SimulacaoInput):
    scenario = next((item for item in listar_cenarios() if item["id"] == dados.cenario_id), None)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Cenário simulado não encontrado")
    segment = next((item for item in listar_trechos() if item["id"] == dados.trecho_id), None)
    if segment is None:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    weather = {
        "trecho_id": dados.trecho_id,
        "fonte": "MOCK_LOCAL",
        "precipitacao_mm": scenario["precipitacao_mm"],
        "intensidade_mm_h": scenario["intensidade_mm_h"],
        "data_hora": now,
        "modo_dados": "mock",
    }
    if DATA_MODE == "mock":
        try:
            weather = registrar_medicao(weather)
        except ValueError as erro:
            existing = next(
                (
                    item for item in listar_medicoes(dados.trecho_id)
                    if item.get("fonte") == weather["fonte"]
                    and item.get("data_hora") == now.isoformat()
                    and item.get("precipitacao_mm") == weather["precipitacao_mm"]
                    and item.get("intensidade_mm_h") == weather["intensidade_mm_h"]
                ),
                None,
            )

            if existing is None:
                raise HTTPException(
                    status_code=409,
                    detail=str(erro),
                ) from erro

            weather = existing
    else:
        weather["id"] = 0  # Simulação isolada: não grava cenário no banco operacional.
    drainage = segment.get("drenagem") or {}
    analysis_data = {
        "trecho_id": dados.trecho_id,
        "dados_clima_id": weather["id"],
        "intensidade_mm_h": scenario["intensidade_mm_h"],
        "precipitacao_mm": scenario["precipitacao_mm"],
        "estado_pavimento": segment.get("estado_pavimento", scenario.get("estado_pavimento")),
        "inclinacao_percentual": segment.get("inclinacao_percentual"),
        "estado_inclinacao": segment.get("estado_inclinacao"),
        "data_hora": now,
        "area_contribuicao_m2": segment.get("area_contribuicao_m2"),
        "coeficiente_escoamento": segment.get("coeficiente_escoamento"),
        "drenagem": drainage,
        "mtd_mm": segment.get("mtd_mm"),
        "caminho_escoamento_m": segment.get("caminho_escoamento_m"),
        "declividade_caminho_percentual": segment.get("declividade_caminho_percentual"),
        "origem_dados": "mock",
    }
    result = analisar_trecho(analysis_data, persistir=DATA_MODE == "mock")
    return {
        "modo_dados": "mock",
        "persistida": DATA_MODE == "mock",
        "cenario": scenario,
        "trecho": {"id": segment["id"], "codigo": segment.get("codigo"), "km_inicial": segment["km_inicial"], "km_final": segment["km_final"]},
        "resultado": result,
    }


@app.get("/health")
def health_check():
    if DATA_MODE == "mock":
        return {"status": "ok", "modo_dados": DATA_MODE, "banco": "não utilizado"}
    verificar_banco()
    return {"status": "ok", "modo_dados": DATA_MODE, "banco": "conectado"}
