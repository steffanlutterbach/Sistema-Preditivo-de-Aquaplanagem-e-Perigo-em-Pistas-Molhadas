"""Rotas de rodovias."""

from fastapi import APIRouter

router = APIRouter(prefix="/rodovias", tags=["rodovias"])


@router.get("")
def listar_rodovias():
    return []
