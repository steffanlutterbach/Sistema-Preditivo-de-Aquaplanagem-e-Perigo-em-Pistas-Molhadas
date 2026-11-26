"""Testes HTTP da API usando ASGI e apenas a biblioteca padrão."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

import pytest

from app.main import app
from app.repositories import resetar_mock
from app.services.calculo_vazao import calcular_lamina_agua, calcular_vazao, calcular_volume


def request(method: str, path: str, payload: dict | None = None, headers: dict[str, str] | None = None):
    encoded = json.dumps(payload).encode() if payload is not None else b""
    parsed = urlsplit(path)
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": method, "scheme": "http", "path": parsed.path, "raw_path": parsed.path.encode(),
        "query_string": parsed.query.encode(),
        "headers": [(b"host", b"test"), *((key.lower().encode(), value.encode()) for key, value in (headers or {}).items())],
        "client": ("test", 1234), "server": ("test", 80),
    }
    sent = []
    received = False

    async def receive():
        nonlocal received
        if not received:
            received = True
            return {"type": "http.request", "body": encoded, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(message for message in sent if message["type"] == "http.response.start")
    body = b"".join(message.get("body", b"") for message in sent if message["type"] == "http.response.body")
    return start["status"], json.loads(body) if body else None


@pytest.fixture(autouse=True)
def clean_mock_state():
    resetar_mock()


def test_cinco_segmentos_br116_e_dados_aproximados():
    status, segments = request("GET", "/trechos")
    assert status == 200
    assert [item["codigo"] for item in segments] == [f"BR116-{km}" for km in range(264, 269)]
    assert all(item["origem_dados"] == "simulado_fornecido_pelo_usuario" for item in segments)
    assert all(item["geometria_validada"] is False for item in segments)


def test_cadastrar_consultar_e_atualizar_segmento():
    payload = {"codigo": "BR116-269", "rodovia_id": 1, "km_inicial": 269, "km_final": 270,
               "comprimento_m": 1000, "inclinacao_percentual": 2.0}
    status, created = request("POST", "/trechos", payload)
    assert status == 201 and created["codigo"] == "BR116-269"
    status, fetched = request("GET", f"/trechos/{created['id']}")
    assert status == 200 and fetched["km_inicial"] == 269
    status, updated = request("PATCH", f"/trechos/{created['id']}", {"inclinacao_percentual": 3.1})
    assert status == 200 and updated["inclinacao_percentual"] == 3.1
    assert request("GET", f"/trechos/{created['id']}")[1]["inclinacao_percentual"] == 3.1


def test_validacao_intervalo_geometria_e_coordenadas():
    invalid_segment = {"codigo": "BAD", "rodovia_id": 1, "km_inicial": 2, "km_final": 1}
    assert request("POST", "/trechos", invalid_segment)[0] == 422
    assert request("POST", "/monitoramento/localizacao", {"latitude": 91, "longitude": 0})[0] == 422


def test_associacao_candidata_precisa_ser_validada_antes_da_medicao():
    assert len(request("GET", "/meteorologia/estacoes?trecho_id=1")[1]) == 3
    payload = {"trecho_id": 1, "fonte": "INMET", "intensidade_mm_h": 8, "estacao_id": 2}
    assert request("POST", "/meteorologia", payload)[0] == 422
    status, association = request("PUT", "/meteorologia/estacoes/2/trechos/1", {"status_associacao": "validada", "justificativa": "associação simulada para teste"})
    assert status == 200 and association["status_associacao"] == "validada"
    assert request("POST", "/meteorologia", payload)[0] == 200


def test_meteorologia_e_identificada_e_duplicidade_rejeitada():
    payload = {"trecho_id": 1, "fonte": "MOCK_TEST", "precipitacao_mm": 5, "intensidade_mm_h": 5,
               "data_hora": datetime.now(timezone.utc).isoformat()}
    status, first = request("POST", "/meteorologia", payload)
    assert status == 200 and first["modo_dados"] == "mock"
    assert request("POST", "/meteorologia", payload)[0] == 409
    listed = request("GET", "/meteorologia?trecho_id=1")[1]
    assert listed[0]["dados_desatualizados"] is False


def test_dados_meteorologicos_antigos_sao_marcados_e_nao_classificados():
    old = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    status, weather = request("POST", "/meteorologia", {"trecho_id": 1, "fonte": "MOCK_TEST",
        "precipitacao_mm": 20, "intensidade_mm_h": 20, "data_hora": old})
    assert status == 200 and weather["dados_desatualizados"] is True
    status, analysis = request("POST", "/analises", {"trecho_id": 1})
    assert status == 200 and analysis["status_analise"] == "dados_desatualizados"
    assert analysis["nivel_risco"] is None and analysis["classificacao_confiavel"] is False


@pytest.mark.parametrize(("scenario_id", "segment_id", "expected"), [(1, 1, "baixo"), (2, 2, "moderado"), (3, 3, "alto")])
def test_cenarios_de_risco(scenario_id, segment_id, expected):
    status, result = request("POST", "/simulacoes", {"cenario_id": scenario_id, "trecho_id": segment_id})
    assert status == 200
    assert result["modo_dados"] == "mock"
    assert result["resultado"]["nivel_risco"] == expected
    assert result["resultado"]["classificacao_confiavel"] is False
    assert result["resultado"]["versao_algoritmo"] == "risk-v1-experimental"
    assert result["resultado"]["origem_dados"] == "mock"


def test_faltam_dados_obrigatorios_sem_classificacao():
    status, result = request("POST", "/meteorologia", {"trecho_id": 1, "fonte": "MOCK_PARTIAL", "intensidade_mm_h": 20})
    assert status == 200
    status, analysis = request("POST", "/analises", {"trecho_id": 1})
    assert status == 200
    assert analysis["status_analise"] == "dados_insuficientes"
    assert analysis["nivel_risco"] is None
    assert "precipitacao_acumulada" in analysis["dados_ausentes"]


def test_wd_e_condicional_e_inclinacao_percentual_e_usada_como_s():
    value = calcular_lamina_agua(0.55, 11.2, 20, 1.5)
    assert value >= 0
    with pytest.raises(ValueError):
        calcular_lamina_agua(0.55, 11.2, 20, 0)
    status, result = request("POST", "/simulacoes", {"cenario_id": 2, "trecho_id": 2})
    assert status == 200 and result["resultado"]["wd_mm"] is not None
    assert result["resultado"]["wd_status"] == "calculada_condicionalmente"
    assert result["resultado"]["dados_utilizados"]["wd_declividade_origem"] == "inclinacao_percentual"


def test_wd_calcula_quando_declividade_do_caminho_esta_disponivel():
    status, _ = request("PATCH", "/trechos/2", {"declividade_caminho_percentual": 1.5})
    assert status == 200
    status, result = request("POST", "/simulacoes", {"cenario_id": 2, "trecho_id": 2})
    assert status == 200
    assert result["resultado"]["wd_mm"] is not None
    assert result["resultado"]["dados_utilizados"]["wd_declividade_origem"] == "declividade_caminho_percentual"


def test_wd_fica_ausente_sem_mtd_sem_bloquear_analise_de_risco():
    payload = {"codigo": "BR116-269", "rodovia_id": 1, "km_inicial": 269, "km_final": 270,
               "area_contribuicao_m2": 10500, "coeficiente_escoamento": 0.9,
               "inclinacao_percentual": 2.0, "estado_pavimento": "regular",
               "drenagem": {"tipo": "boca de lobo", "quantidade": 2, "capacidade_total_l_s": 100}}
    status, segment = request("POST", "/trechos", payload)
    assert status == 201
    status, result = request("POST", "/simulacoes", {"cenario_id": 2, "trecho_id": segment["id"]})
    assert status == 200
    assert result["resultado"]["nivel_risco"] == "moderado"
    assert result["resultado"]["wd_mm"] is None
    assert "mtd_mm" in result["resultado"]["wd_dados_ausentes"]


def test_formula_hidrologica_existente():
    assert calcular_vazao(0.8, 35, 1000) == pytest.approx(7.7777777778)
    assert calcular_volume(5, 100, 0.8) == 400


def test_alerta_tem_validade_chave_estavel_e_historico():
    _, first = request("POST", "/simulacoes", {"cenario_id": 3, "trecho_id": 3})
    alert1 = first["resultado"]["alerta"]
    _, second = request("POST", "/simulacoes", {"cenario_id": 3, "trecho_id": 3})
    alert2 = second["resultado"]["alerta"]
    assert alert1["id"] == alert2["id"]
    assert alert1["validade"]
    assert len(request("GET", "/alertas?trecho_id=3")[1]) == 1
    assert len(request("GET", "/alertas?trecho_id=3&historico=true")[1]) == 1


def test_mudanca_para_baixo_resolve_alerta_anterior():
    request("POST", "/simulacoes", {"cenario_id": 3, "trecho_id": 3})
    status, result = request("POST", "/analises", {"trecho_id": 3, "intensidade_mm_h": 5,
        "precipitacao_mm": 5, "estado_pavimento": "bom"})
    assert status == 200 and result["nivel_risco"] == "baixo"
    assert request("GET", "/alertas?trecho_id=3")[1] == []
    history = request("GET", "/alertas?trecho_id=3&historico=true")[1]
    assert history[0]["status"] == "resolvido"


def test_localizacao_encontra_segmento_sem_reter_coordenada():
    status, result = request("POST", "/monitoramento/localizacao", {
        "latitude": -23.59515, "longitude": -46.73625, "sentido": "crescente"})
    assert status == 200
    assert result["segmento_atual"]["codigo"] == "BR116-264"
    assert result["localizacao_armazenada"] is False
    assert result["proximos_segmentos"][0]["codigo"] == "BR116-265"


def test_localizacao_fora_da_tolerancia_nao_afirma_segmento_atual():
    status, result = request("POST", "/monitoramento/localizacao", {"latitude": 0, "longitude": 0})
    assert status == 200 and result["status"] == "fora_da_tolerancia"
    assert result["segmento_atual"] is None
    assert result["proximos_segmentos"] == []


def test_alerta_do_proximo_segmento_e_retornado_com_distancia():
    request("POST", "/simulacoes", {"cenario_id": 3, "trecho_id": 2})
    _, result = request("POST", "/monitoramento/localizacao", {
        "latitude": -23.59515, "longitude": -46.73625, "sentido": "crescente"})
    assert any(item["trecho_id"] == 2 and item["distancia_ate_trecho_m"] > 0 for item in result["alertas_relevantes"])


def test_health_and_map_have_consistent_mock_data():
    status, health = request("GET", "/health")
    assert status == 200 and health["modo_dados"] == "mock"
    status, feature_collection = request("GET", "/mapa/riscos")
    assert status == 200 and len(feature_collection["features"]) == 5
    assert feature_collection["features"][0]["geometry"]["type"] == "LineString"


def test_chave_de_api_e_exigida_quando_configurada(monkeypatch):
    import app.main as main_module

    monkeypatch.setattr(main_module, "API_KEY", "chave-de-teste")
    assert request("GET", "/health")[0] == 401
    assert request("GET", "/health", headers={"X-API-Key": "errada"})[0] == 401
    status, _ = request("GET", "/health", headers={"X-API-Key": "chave-de-teste"})
    assert status == 200


def test_falha_de_banco_retorna_503_sem_expor_detalhes(monkeypatch):
    import app.main as main_module
    import psycopg

    monkeypatch.setattr(main_module, "API_KEY", "")
    monkeypatch.setattr(main_module, "DATA_MODE", "real")
    monkeypatch.setattr(main_module, "verificar_banco", lambda: (_ for _ in ()).throw(psycopg.OperationalError("senha secreta")))
    status, body = request("GET", "/health")
    assert status == 503
    assert "senha secreta" not in body["detail"]


def test_simulacao_em_modo_real_nao_persiste_no_banco_operacional(monkeypatch):
    import app.main as main_module
    from app.repositories import listar_analises

    monkeypatch.setattr(main_module, "API_KEY", "")
    monkeypatch.setattr(main_module, "DATA_MODE", "real")
    status, result = request("POST", "/simulacoes", {"cenario_id": 3, "trecho_id": 3})
    assert status == 200 and result["persistida"] is False
    assert listar_analises(3) == []


def test_migrations_preservam_tabelas_e_incluem_cinco_segmentos():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    migration = (root / "database" / "migrations" / "003_seed_br116_mock.sql").read_text(encoding="utf-8")
    schema_changes = (root / "database" / "migrations" / "002_backend_monitoramento.sql").read_text(encoding="utf-8")
    for kilometer in range(264, 269):
        assert f"BR116-{kilometer}" in migration
    assert "DROP TABLE" not in migration.upper()
    assert "DROP TABLE" not in schema_changes.upper()
    assert "ADD COLUMN IF NOT EXISTS" in schema_changes
