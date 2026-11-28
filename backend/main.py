
from fastapi import FastAPI
from database import testar_conexao

app = FastAPI(
    title="AquaSafe API",
    description="Sistema Preditivo de Aquaplanagem e Perigo em Pistas Molhadas",
    version="1.0.0"
)


@app.get("/")
def inicio():
    return {
        "sistema": "AquaSafe",
        "mensagem": "API funcionando corretamente!"
    }


@app.get("/banco")
def verificar_banco():
    try:
        banco = testar_conexao()

        return {
            "status": "conectado",
            "banco": banco
        }

    except Exception as erro:
        return {
            "status": "erro",
            "mensagem": str(erro)
        }
