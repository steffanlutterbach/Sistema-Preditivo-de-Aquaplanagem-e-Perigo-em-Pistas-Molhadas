"""Cálculos hidrológicos iniciais."""


def calcular_vazao(coeficiente: float, intensidade_mm_h: float, area_m2: float) -> float:
    if coeficiente < 0 or coeficiente > 1:
        raise ValueError("Coeficiente de escoamento deve estar entre 0 e 1")
    if intensidade_mm_h < 0 or area_m2 <= 0:
        raise ValueError("Intensidade e área devem ser válidas")
    return (coeficiente * intensidade_mm_h * area_m2) / 3600


def calcular_volume(precipitacao_mm: float, area_m2: float, coeficiente: float) -> float:
    if precipitacao_mm < 0 or area_m2 <= 0 or coeficiente < 0 or coeficiente > 1:
        raise ValueError("Parâmetros inválidos para cálculo do volume")
    return precipitacao_mm * area_m2 * coeficiente
