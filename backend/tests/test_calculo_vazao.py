
from app.services.calculo_vazao import calcular_vazao
from app.services.classificacao_risco import analisar_trecho


def test_calcula_vazao():
    assert calcular_vazao(0.8, 35, 1000) == 7.777777777777778


def criar_dados_teste(capacidade_drenagem):
    return {
        "trecho_id": 1,
        "dados_clima_id": 1,
        "intensidade_mm_h": 20,
        "precipitacao_mm": 10,
        "estado_pavimento": "bom",
        "area_contribuicao_m2": 10500,
        "coeficiente_escoamento": 0.9,
        "drenagem": {
            "capacidade_total_l_s": capacidade_drenagem
        },
        "origem_dados": "mock",
    }


def test_drenagem_suficiente():
    dados = criar_dados_teste(100)

    resultado = analisar_trecho(dados, persistir=False)

    assert resultado["vazao_estimada_l_s"] == 52.5
    assert resultado["dados_utilizados"]["drenagem_suficiente"] is True
    assert resultado["pontuacao_risco"] == 40


def test_drenagem_insuficiente():
    dados = criar_dados_teste(40)

    resultado = analisar_trecho(dados, persistir=False)

    assert resultado["vazao_estimada_l_s"] == 52.5
    assert resultado["dados_utilizados"]["drenagem_suficiente"] is False
    assert resultado["pontuacao_risco"] == 55



def test_classificacao_indisponivel_sem_capacidade_drenagem():
    dados = criar_dados_teste(None)

    resultado = analisar_trecho(dados, persistir=False)

    assert resultado["dados_utilizados"]["drenagem_suficiente"] is None
    assert resultado["pontuacao_risco"] is None
    assert resultado["nivel_risco"] is None
    assert resultado["status_analise"] == "dados_insuficientes"
    assert "capacidade_drenagem" in resultado["dados_ausentes"]

def test_aumento_da_chuva_aumenta_o_risco():
    dados = {
        "trecho_id": 1,
        "dados_clima_id": 1,
        "intensidade_mm_h": 5,
        "precipitacao_mm": 10,
        "estado_pavimento": "bom",
        "area_contribuicao_m2": 10500,
        "coeficiente_escoamento": 0.85,
        "drenagem": {
            "capacidade_total_l_s": 600
        },
        "origem_dados": "mock",
    }

    resultados = []

    for intensidade in [5, 20, 35]:
        dados["intensidade_mm_h"] = intensidade
        resultado = analisar_trecho(dados, persistir=False)
        resultados.append(resultado)

    assert resultados[0]["pontuacao_risco"] == 10
    assert resultados[0]["nivel_risco"] == "baixo"

    assert resultados[1]["pontuacao_risco"] == 40
    assert resultados[1]["nivel_risco"] == "moderado"

    assert resultados[2]["pontuacao_risco"] == 70
    assert resultados[2]["nivel_risco"] == "alto"

def test_drenagem_exatamente_igual_a_vazao():
    dados = criar_dados_teste(52.5)

    resultado = analisar_trecho(dados, persistir=False)

    assert resultado["vazao_estimada_l_s"] == 52.5
    assert resultado["dados_utilizados"]["drenagem_suficiente"] is True
    assert resultado["pontuacao_risco"] == 40
    assert resultado["nivel_risco"] == "moderado"