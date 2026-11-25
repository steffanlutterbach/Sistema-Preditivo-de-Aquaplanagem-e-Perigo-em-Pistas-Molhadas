"""Rotas de trechos."""

from fastapi import APIRouter

router = APIRouter(prefix="/trechos", tags=["trechos"])


@router.get("")
def listar_trechos():
    return []


@router.get("/{trecho_id}")
def consultar_trecho(trecho_id: int):
    return {"id": trecho_id}


@router.get("/{trecho_id}/risco")
def consultar_risco(trecho_id: int):
    return {"trecho_id": trecho_id, "nivel_risco": "baixo"}
