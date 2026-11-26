"""Consulta de alertas ativos e do histórico por segmento."""

from fastapi import APIRouter, HTTPException, Query

from app.repositories import consultar_trecho, listar_alertas as obter_alertas

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("")
def listar_alertas(trecho_id: int | None = Query(default=None, gt=0), historico: bool = False):
    if trecho_id is not None and consultar_trecho(trecho_id) is None:
        raise HTTPException(status_code=404, detail="Trecho não encontrado")
    return obter_alertas(trecho_id=trecho_id, historico=historico)
