"""Cadastro e consulta dos segmentos rodoviários."""

from fastapi import APIRouter, HTTPException, Query

from app.core.config import DATA_MODE
from app.repositories import (
    atualizar_trecho, consultar_trecho, criar_trecho, listar_analises,
    listar_estacoes, listar_rodovias, listar_trechos, dados_desatualizados,
)
from app.schemas import TrechoInput, TrechoUpdateInput

router = APIRouter(prefix="/trechos", tags=["trechos"])


@router.get("")
def consultar_trechos(rodovia_id: int | None = Query(default=None, gt=0)):
    items = listar_trechos()
    return items if rodovia_id is None else [item for item in items if item["rodovia_id"] == rodovia_id]


@router.post("", status_code=201)
def cadastrar_trecho(dados: TrechoInput):
    if not any(item["id"] == dados.rodovia_id for item in listar_rodovias()):
        raise HTTPException(status_code=404, detail="Rodovia não encontrada")
    payload = dados.model_dump(exclude_none=True)
    if DATA_MODE == "mock":
        payload["origem_dados"] = "mock"
        payload["geometria_validada"] = False
    try:
        return criar_trecho(payload)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro


@router.get("/{trecho_id}")
def consultar_trecho_por_id(trecho_id: int):
    trecho = consultar_trecho(trecho_id)
    if trecho is None:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return trecho


@router.patch("/{trecho_id}")
def atualizar_trecho_por_id(trecho_id: int, dados: TrechoUpdateInput):
    atual = consultar_trecho(trecho_id)
    if atual is None:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    changes = dados.model_dump(exclude_unset=True, exclude_none=True)
    if DATA_MODE == "mock":
        changes["origem_dados"] = "mock"
        changes["geometria_validada"] = False
    merged = {**atual, **changes}
    if float(merged["km_final"]) <= float(merged["km_inicial"]):
        raise HTTPException(status_code=422, detail="km_final deve ser maior que km_inicial")
    if "rodovia_id" in changes and not any(r["id"] == changes["rodovia_id"] for r in listar_rodovias()):
        raise HTTPException(status_code=404, detail="Rodovia não encontrada")
    if "geometria" in changes:
        geometry = changes["geometria"]
        if geometry.get("type") != "LineString" or len(geometry.get("coordinates", [])) < 2:
            raise HTTPException(status_code=422, detail="geometria deve ser um GeoJSON LineString com dois pontos ou mais")
        for coord in geometry["coordinates"]:
            if len(coord) < 2 or not -180 <= coord[0] <= 180 or not -90 <= coord[1] <= 90:
                raise HTTPException(status_code=422, detail="coordenadas GeoJSON devem seguir [longitude, latitude]")
    try:
        result = atualizar_trecho(trecho_id, changes)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    return result


@router.get("/{trecho_id}/estacoes")
def consultar_estacoes_do_trecho(trecho_id: int):
    consultar_trecho_por_id(trecho_id)
    return listar_estacoes(trecho_id)


@router.get("/{trecho_id}/risco")
def consultar_risco(trecho_id: int):
    consultar_trecho_por_id(trecho_id)
    analyses = listar_analises(trecho_id)
    if not analyses:
        return {"trecho_id": trecho_id, "status_analise": "sem_analises", "nivel_risco": None}
    latest = analyses[0]
    stale = dados_desatualizados(latest.get("data_analise"))
    if stale:
        latest = {**latest, "nivel_risco": None, "status_analise": "dados_desatualizados",
                  "dados_desatualizados": True, "classificacao_disponivel": False}
    return latest
