"""Classificação experimental de risco."""


def classificar_risco(pontuacao: float) -> str:
    if not 0 <= pontuacao <= 100:
        raise ValueError("A pontuação deve estar entre 0 e 100")
    if pontuacao < 35:
        return "baixo"
    if pontuacao < 70:
        return "moderado"
    return "alto"
