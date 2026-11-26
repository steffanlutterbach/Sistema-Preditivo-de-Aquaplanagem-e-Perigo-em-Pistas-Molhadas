"""Rotas de rodovias."""

from fastapi import APIRouter
from app.repositories import listar_rodovias as obter_rodovias

router = APIRouter(prefix="/rodovias", tags=["rodovias"])


@router.get("")
def listar_rodovias():
    return obter_rodovias()
