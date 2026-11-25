"""Rotas de alertas."""

from fastapi import APIRouter

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("")
def listar_alertas():
    return []
