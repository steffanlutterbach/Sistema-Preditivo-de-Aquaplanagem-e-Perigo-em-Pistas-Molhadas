"""Consulta de risco por localização enviada pelo aplicativo.

As coordenadas são processadas em memória durante a requisição e não são persistidas.
"""

from fastapi import APIRouter

from app.schemas import LocalizacaoInput
from app.services.monitoramento import consultar_riscos_proximos

router = APIRouter(prefix="/monitoramento", tags=["monitoramento"])


@router.post("/localizacao")
def processar_localizacao(dados: LocalizacaoInput):
    return consultar_riscos_proximos(dados.latitude, dados.longitude, dados.sentido)
