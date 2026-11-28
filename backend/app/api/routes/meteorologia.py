"""Rotas de dados meteorológicos."""

from fastapi import APIRouter, HTTPException
from app.integrations.meteorologia import normalizar_observacao
from app.core.config import DATA_MODE
from app.repositories import associar_estacao, criar_estacao, listar_estacoes, listar_medicoes, listar_trechos, registrar_medicao
from app.schemas import (
    AssociacaoEstacaoInput,
    EstacaoMeteorologicaInput,
    MedicaoMeteorologicaInput,
    MedicaoExternaInput,
)

router = APIRouter(prefix="/meteorologia", tags=["meteorologia"])


@router.post("")
def registrar_meteorologia(dados: MedicaoMeteorologicaInput):
    if not any(trecho["id"] == dados.trecho_id for trecho in listar_trechos()):
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    medicao = dados.model_dump()
    medicao["modo_dados"] = "mock" if medicao.get("fonte", "").upper().startswith("MOCK") else None
    if medicao["modo_dados"] is None:
        medicao.pop("modo_dados")
    if medicao.get("estacao_id") is not None:
        station = next((item for item in listar_estacoes(dados.trecho_id) if item.get("id") == dados.estacao_id), None)
        if station is None:
            raise HTTPException(status_code=422, detail="Estação não associada ao trecho")
        if station.get("status_associacao") != "validada":
            raise HTTPException(status_code=422, detail="Associação da estação ainda não foi validada")
    medicao["data_hora"] = dados.data_hora
    try:
        return registrar_medicao(medicao)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro

@router.post("/externa")
def registrar_meteorologia_externa(dados: MedicaoExternaInput):
    if not any(
        trecho["id"] == dados.trecho_id
        for trecho in listar_trechos()
    ):
        raise HTTPException(status_code=404, detail="Trecho não encontrado")

    if dados.estacao_id is not None:
        station = next(
            (
                item for item in listar_estacoes(dados.trecho_id)
                if item.get("id") == dados.estacao_id
            ),
            None,
        )

        if station is None:
            raise HTTPException(
                status_code=422,
                detail="Estação não associada ao trecho",
            )

        if station.get("status_associacao") != "validada":
            raise HTTPException(
                status_code=422,
                detail="Associação da estação ainda não foi validada",
            )

    try:
        medicao = normalizar_observacao(
            fonte=dados.fonte,
            dados={
                "precipitacao_mm": dados.precipitacao_mm,
                "data_hora": dados.data_hora,
                "identificador_externo": dados.identificador_externo,
            },
            trecho_id=dados.trecho_id,
            estacao_id=dados.estacao_id,
        )

        return registrar_medicao(medicao)

    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro


@router.get("")
def consultar_medicoes(trecho_id: int | None = None):
    if trecho_id is not None and not any(trecho["id"] == trecho_id for trecho in listar_trechos()):
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return listar_medicoes(trecho_id)


@router.get("/estacoes")
def consultar_estacoes(trecho_id: int | None = None):
    if trecho_id is not None and not any(trecho["id"] == trecho_id for trecho in listar_trechos()):
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return listar_estacoes(trecho_id)


@router.post("/estacoes", status_code=201)
def cadastrar_estacao(dados: EstacaoMeteorologicaInput):
    try:
        payload = dados.model_dump(exclude_none=True)
        payload.setdefault("origem_dados", DATA_MODE)
        return criar_estacao(payload)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro


@router.put("/estacoes/{estacao_id}/trechos/{trecho_id}")
def definir_associacao_estacao(estacao_id: int, trecho_id: int, dados: AssociacaoEstacaoInput):
    if not any(t["id"] == trecho_id for t in listar_trechos()):
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    result = associar_estacao(trecho_id, estacao_id, dados.model_dump(exclude_none=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Estação não encontrada")
    return result
