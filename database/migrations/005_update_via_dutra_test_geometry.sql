-- Atualiza a segunda regiao mock com coordenadas, coeficientes e associacoes
-- fornecidos no JSON de teste do usuario. Nao e dado meteorologico ao vivo.
-- Aplicar depois da migration 004.

BEGIN;

WITH road AS (
    SELECT id FROM rodovias
    WHERE nome = 'BR-116 - Via Dutra (segmentos demonstrativos, km 225-230)'
      AND estado = 'SP'
), data(codigo_antigo, codigo_novo, km_i, km_f, largura, area, coeficiente,
        inclinacao, mtd, caminho, pavimento, drenagem_qtd, drenagem_individual,
        drenagem_total, geometria_wkt, expectativa) AS (VALUES
    ('T-225', 'BR116-SP-225-226', 225.00, 226.00, 14.00, 14000.000, 0.850, 1.200, 0.750, 14.2, 'bom',       14, 30.0, 420.0,
     'LINESTRING(-46.57845 -23.51412,-46.58180 -23.51535,-46.58520 -23.51658,-46.58815 -23.51765)', 'Risco moderado: pista larga reduz velocidade do escoamento.'),
    ('T-226', 'BR116-SP-226-227', 226.00, 227.00, 14.50, 14500.000, 0.880, 0.800, 0.550, 14.8, 'regular',   12, 25.0, 300.0,
     'LINESTRING(-46.58815 -23.51765,-46.59140 -23.51862,-46.59475 -23.51938,-46.59790 -23.51985)', 'Risco alto: varzea muito plana proxima ao Trevo Fernao Dias.'),
    ('T-227', 'BR116-SP-227-228', 227.00, 228.00, 15.00, 15000.000, 0.920, 0.600, 0.400, 15.2, 'irregular', 10, 20.0, 200.0,
     'LINESTRING(-46.59790 -23.51985,-46.60120 -23.51995,-46.60455 -23.51965,-46.60765 -23.51910)', 'Risco alto critico: ponto baixo de acumulo e microtextura gasta.'),
    ('T-228', 'BR116-SP-228-229', 228.00, 229.00, 14.00, 14000.000, 0.880, 1.000, 0.600, 14.2, 'regular',   14, 25.0, 350.0,
     'LINESTRING(-46.60765 -23.51910,-46.61085 -23.51845,-46.61410 -23.51782,-46.61735 -23.51730)', 'Risco moderado: transicao da Ponte da Vila Guilherme.'),
    ('T-229', 'BR116-SP-229-230', 229.00, 230.00, 14.00, 14000.000, 0.850, 1.500, 0.800, 14.2, 'bom',      16, 30.0, 480.0,
     'LINESTRING(-46.61735 -23.51730,-46.62060 -23.51695,-46.62390 -23.51680,-46.62715 -23.51685)', 'Risco baixo/moderado: melhor caimento no acesso a Marginal.')
), updated AS (
    UPDATE trechos t SET
        codigo = d.codigo_novo,
        rodovia_id = road.id,
        km_inicial = d.km_i,
        km_final = d.km_f,
        comprimento = 1000.0,
        largura = d.largura,
        area_contribuicao_m2 = d.area,
        coeficiente_escoamento = d.coeficiente,
        inclinacao = d.inclinacao,
        inclinacao_unidade = '%',
        estado_inclinacao = 'Declividade longitudinal informada para teste',
        mtd_mm = d.mtd,
        caminho_escoamento_m = d.caminho,
        declividade_caminho_pct = NULL,
        geometria = ST_SetSRID(ST_GeomFromText(d.geometria_wkt), 4326),
        geometria_validada = TRUE,
        origem_dados = 'mock',
        origem_geometria = 'Coordenadas fornecidas no JSON mock do usuario; sem verificacao independente.'
    FROM data d, road
    WHERE t.codigo = d.codigo_antigo
    RETURNING t.id, t.codigo
)
SELECT count(*) FROM updated;

WITH data(codigo, pavimentacao, estado, tipo, quantidade, capacidade_individual,
          capacidade_total, expectativa) AS (VALUES
    ('BR116-SP-225-226', 'CAUQ (Asfalto)', 'bom',       'Boca de lobo dupla',   14, 30.0, 420.0, 'Risco moderado: pista larga reduz velocidade do escoamento.'),
    ('BR116-SP-226-227', 'CAUQ (Asfalto)', 'regular',   'Boca de lobo simples', 12, 25.0, 300.0, 'Risco alto: varzea muito plana proxima ao Trevo Fernao Dias.'),
    ('BR116-SP-227-228', 'CAUQ (Asfalto)', 'irregular', 'Boca de lobo simples', 10, 20.0, 200.0, 'Risco alto critico: ponto baixo de acumulo e microtextura gasta.'),
    ('BR116-SP-228-229', 'CAUQ (Asfalto)', 'regular',   'Boca de lobo dupla',   14, 25.0, 350.0, 'Risco moderado: transicao da Ponte da Vila Guilherme.'),
    ('BR116-SP-229-230', 'CAUQ (Asfalto)', 'bom',       'Boca de lobo dupla',   16, 30.0, 480.0, 'Risco baixo/moderado: melhor caimento no acesso a Marginal.')
)
UPDATE condicoes_pista cp SET
    pavimentacao = d.pavimentacao,
    estado_pavimento = d.estado,
    observacoes = 'Dados mock fornecidos para teste. Expectativa declarada: ' || d.expectativa || ' Nao e resultado garantido pelo algoritmo atual.'
FROM data d JOIN trechos t ON t.codigo = d.codigo
WHERE cp.trecho_id = t.id;

WITH data(codigo, tipo, quantidade, capacidade_individual, capacidade_total) AS (VALUES
    ('BR116-SP-225-226', 'Boca de lobo dupla',   14, 30.0, 420.0),
    ('BR116-SP-226-227', 'Boca de lobo simples', 12, 25.0, 300.0),
    ('BR116-SP-227-228', 'Boca de lobo simples', 10, 20.0, 200.0),
    ('BR116-SP-228-229', 'Boca de lobo dupla',   14, 25.0, 350.0),
    ('BR116-SP-229-230', 'Boca de lobo dupla',   16, 30.0, 480.0)
)
UPDATE drenagem dr SET
    tipo = d.tipo,
    quantidade = d.quantidade,
    capacidade_individual = d.capacidade_individual,
    capacidade_total = d.capacidade_total,
    observacoes = 'Dados de drenagem mock fornecidos pelo usuario para teste.'
FROM data d JOIN trechos t ON t.codigo = d.codigo
WHERE dr.trecho_id = t.id;

INSERT INTO estacoes_meteorologicas (codigo_externo, fonte_id, nome, ativa, origem_dados, observacoes)
SELECT s.codigo, f.id, s.nome, TRUE, 'mock',
       'Estacao e associacao declaradas validadas no JSON de teste; sem coordenadas nem feed ao vivo.'
FROM (VALUES
    ('355030885A', 'Vila Maria / Parque Novo Mundo'),
    ('355030843A', 'Santana / Carandiru')
) AS s(codigo, nome)
JOIN fontes_dados f ON f.nome = 'Cemaden'
ON CONFLICT (fonte_id, codigo_externo) DO UPDATE SET
    nome = EXCLUDED.nome,
    ativa = TRUE,
    origem_dados = 'mock',
    observacoes = EXCLUDED.observacoes;

WITH links(codigo_trecho, codigo_estacao, justificativa) AS (VALUES
    ('BR116-SP-225-226', '355030885A', 'Associacao validada para teste, conforme JSON fornecido; sem coordenada da estacao.'),
    ('BR116-SP-226-227', '355030885A', 'Associacao validada para teste, conforme JSON fornecido; sem coordenada da estacao.'),
    ('BR116-SP-227-228', '355030885A', 'Associacao validada para teste, conforme JSON fornecido; sem coordenada da estacao.'),
    ('BR116-SP-228-229', '355030843A', 'Associacao validada para teste, conforme JSON fornecido; sem coordenada da estacao.'),
    ('BR116-SP-229-230', '355030843A', 'Associacao validada para teste, conforme JSON fornecido; sem coordenada da estacao.')
)
INSERT INTO trechos_estacoes (trecho_id, estacao_id, status_associacao, justificativa)
SELECT t.id, e.id, 'validada', l.justificativa
FROM links l
JOIN trechos t ON t.codigo = l.codigo_trecho
JOIN estacoes_meteorologicas e ON e.codigo_externo = l.codigo_estacao
JOIN fontes_dados f ON f.id = e.fonte_id AND f.nome = 'Cemaden'
ON CONFLICT (trecho_id, estacao_id) DO UPDATE SET
    status_associacao = EXCLUDED.status_associacao,
    justificativa = EXCLUDED.justificativa;

COMMIT;
