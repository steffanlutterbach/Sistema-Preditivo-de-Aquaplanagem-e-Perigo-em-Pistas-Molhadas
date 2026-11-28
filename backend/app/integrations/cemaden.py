"""Normalização de dados meteorológicos do CEMADEN."""

from datetime import datetime, timezone
from typing import Any


def normalizar_observacao(
    dados: dict[str, Any],
    trecho_id: int,
    estacao_id: int | None = None,
) -> dict[str, Any]:
    """Converte uma observação do CEMADEN para o formato do AquaSafe."""

    precipitacao = dados.get("precipitacao_mm")

    if precipitacao in (None, "", "9999"):
        raise ValueError("Precipitação ausente ou inválida")

    try:
        precipitacao = float(precipitacao)
    except (TypeError, ValueError) as erro:
        raise ValueError("Precipitação deve ser numérica") from erro

    if not 0 <= precipitacao < 9999:
        raise ValueError("Precipitação fora do intervalo permitido")

    data_hora = dados.get("data_hora")

    if not data_hora:
        raise ValueError("Data e hora da observação são obrigatórias")

    if isinstance(data_hora, str):
        try:
            data_hora = datetime.fromisoformat(
                data_hora.replace("Z", "+00:00")
            )
        except ValueError as erro:
            raise ValueError("Data e hora inválidas") from erro

    if not isinstance(data_hora, datetime):
        raise ValueError("Data e hora devem ser válidas")

    if data_hora.tzinfo is None:
        raise ValueError("Data e hora devem possuir fuso horário")

    return {
        "trecho_id": trecho_id,
        "fonte": "CEMADEN",
        "precipitacao_mm": precipitacao,
        "intensidade_mm_h": None,
        "data_hora": data_hora.astimezone(timezone.utc),
        "estacao_id": estacao_id,
        "identificador_externo": dados.get("identificador_externo"),
    }