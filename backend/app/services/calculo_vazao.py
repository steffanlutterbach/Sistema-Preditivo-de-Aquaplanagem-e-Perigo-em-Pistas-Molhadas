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


def calcular_lamina_agua(mtd_mm: float, caminho_m: float, intensidade_mm_h: float, declividade_pct: float) -> float:
    """Estimativa condicional de WD; a declividade de entrada é percentual.

    A expressão do planejamento requer S em m/m, então percentuais são
    convertidos para razão. O chamador só deve usar o resultado quando todos
    os parâmetros estiverem medidos e a declividade representar o caminho
    superficial de escoamento.
    """
    if mtd_mm <= 0 or caminho_m <= 0 or intensidade_mm_h < 0 or declividade_pct <= 0:
        raise ValueError("Parâmetros inválidos para cálculo de WD")
    slope_ratio = declividade_pct / 100
    wd = 0.01485 * (mtd_mm**0.11 * caminho_m**0.43 * intensidade_mm_h**0.59) / (slope_ratio**0.42) - mtd_mm
    return max(0.0, wd)
