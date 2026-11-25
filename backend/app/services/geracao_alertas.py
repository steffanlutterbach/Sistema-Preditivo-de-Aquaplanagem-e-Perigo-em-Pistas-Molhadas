"""Geração experimental de alertas."""


def gerar_alerta(nivel_risco: str, trecho_id: int) -> dict:
    if nivel_risco not in {"baixo", "moderado", "alto"}:
        raise ValueError("Nível de risco inválido")
    return {
        "trecho_id": trecho_id,
        "nivel": nivel_risco,
        "status": "ativo",
        "mensagem": f"Risco {nivel_risco} identificado no trecho {trecho_id}.",
    }
