"""Ponto de entrada da API AquaSafe."""

from fastapi import FastAPI
from app.api.routes import alertas, analises, meteorologia, rodovias, trechos

app = FastAPI(
    title="AquaSafe",
    description="API experimental de monitoramento de risco de aquaplanagem",
    version="0.1.0",
)

app.include_router(rodovias.router)
app.include_router(trechos.router)
app.include_router(meteorologia.router)
app.include_router(analises.router)
app.include_router(alertas.router)


@app.get("/mapa/riscos")
def mapa_riscos():
    return []


@app.post("/simulacoes")
def executar_simulacao(dados: dict):
    return {"modo_dados": "mock", "cenario": dados}


@app.get("/health")
def health_check():
    return {"status": "ok"}
