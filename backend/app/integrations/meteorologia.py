"""Seleção e normalização de fontes meteorológicas."""

from typing import Any

from app.integrations import cemaden, inmet


def normalizar_observacao(
    fonte: str,
    dados: dict[str, Any],
    trecho_id: int,
    estacao_id: int | None = None,
) -> dict[str, Any]:
    """Seleciona o adaptador conforme a fonte meteorológica."""

    fonte_normalizada = fonte.strip().upper()

    if fonte_normalizada == "INMET":
        return inmet.normalizar_observacao(
            dados, trecho_id, estacao_id
        )

    if fonte_normalizada == "CEMADEN":
        return cemaden.normalizar_observacao(
            dados, trecho_id, estacao_id
        )

    raise ValueError(f"Fonte meteorológica não suportada: {fonte}")