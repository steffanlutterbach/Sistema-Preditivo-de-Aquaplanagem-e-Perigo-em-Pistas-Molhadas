"""Rotas de análises de risco."""

from fastapi import APIRouter

router = APIRouter(prefix="/analises", tags=["analises"])


@router.post("")
def executar_analise(dados: dict):
    return {"dados": dados, "nivel_risco": "moderado"}
