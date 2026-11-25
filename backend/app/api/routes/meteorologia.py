"""Rotas de dados meteorológicos."""

from fastapi import APIRouter

router = APIRouter(prefix="/meteorologia", tags=["meteorologia"])


@router.post("")
def registrar_meteorologia(dados: dict):
    return dados
