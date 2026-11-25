from app.services.calculo_vazao import calcular_vazao


def test_calcula_vazao():
    assert calcular_vazao(0.8, 35, 1000) == 7.777777777777778
