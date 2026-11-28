-- Segunda regiao demonstrativa da BR-116 (Via Dutra), km 225-230.
-- Dados e associacoes informados para teste, sem geometrias de trecho ou
-- coordenadas de estacao; nao representam levantamento ou integracao real.
-- Aplicar depois de 001_initial_schema.sql e 002_backend_monitoramento.sql.

BEGIN;

INSERT INTO rodovias (nome, estado, descricao)
VALUES (
    'BR-116 - Via Dutra (segmentos demonstrativos, km 225-230)',
    'SP',
    'Segunda regiao de teste. Parametros fornecidos para simulacao; geometrias e cobertura meteorologica nao verificadas em campo.'
)
ON CONFLICT (nome, estado) DO NOTHING;

WITH road AS (
    SELECT id FROM rodovias
    WHERE nome = 'BR-116 - Via Dutra (segmentos demonstrativos, km 225-230)'
      AND estado = 'SP'
), seed(codigo, km_i, km_f, largura, area, inclinacao, pavimento, mtd, caminho,
       drenagem_qtd, drenagem_individual, drenagem_total) AS (VALUES
    ('T-225', 225.00, 226.00, 14.00, 14000.000, 1.200, 'bom',       0.750, 14.2, 14, 30.0, 420.0),
    ('T-226', 226.00, 227.00, 14.50, 14500.000, 0.800, 'regular',  0.550, 14.8, 12, 25.0, 300.0),
    ('T-227', 227.00, 228.00, 15.00, 15000.000, 0.600, 'irregular',0.400, 15.2, 10, 20.0, 200.0),
    ('T-228', 228.00, 229.00, 14.00, 14000.000, 1.000, 'regular',  0.600, 14.2, 14, 25.0, 350.0),
    ('T-229', 229.00, 230.00, 14.00, 14000.000, 1.500, 'bom',      0.800, 14.2, 16, 30.0, 480.0)
), inserted AS (
    INSERT INTO trechos (
        codigo, rodovia_id, km_inicial, km_final, comprimento, largura,
        area_contribuicao_m2, coeficiente_escoamento, inclinacao,
        inclinacao_unidade, estado_inclinacao, mtd_mm, caminho_escoamento_m,
        geometria, geometria_validada, origem_dados, origem_geometria
    )
    SELECT s.codigo, road.id, s.km_i, s.km_f, 1000.0, s.largura, s.area,
           0.900, s.inclinacao, '%', 'Declividade longitudinal informada para teste',
           s.mtd, s.caminho, NULL, FALSE, 'mock',
           'Geometria nao fornecida; nao usar em correspondencia espacial.'
    FROM seed s CROSS JOIN road
    ON CONFLICT (codigo) WHERE codigo IS NOT NULL DO NOTHING
    RETURNING id, codigo
)
SELECT count(*) FROM inserted;

DO $$
DECLARE
    item RECORD;
    target_id INTEGER;
BEGIN
    FOR item IN SELECT * FROM (VALUES
        ('T-225', 'CAUQ', 'bom',       'Drenagem urbana simulada', 14, 30.0, 420.0, 'Risco moderado: pista larga reduz velocidade do escoamento.'),
        ('T-226', 'CAUQ', 'regular',   'Drenagem urbana simulada', 12, 25.0, 300.0, 'Risco alto: varzea muito plana proxima ao Trevo Fernao Dias.'),
        ('T-227', 'CAUQ', 'irregular', 'Drenagem urbana simulada', 10, 20.0, 200.0, 'Risco alto critico: ponto baixo de acumulo e microtextura gasta.'),
        ('T-228', 'CAUQ', 'regular',   'Drenagem urbana simulada', 14, 25.0, 350.0, 'Risco moderado: transicao da Ponte da Vila Guilherme.'),
        ('T-229', 'CAUQ', 'bom',       'Drenagem urbana simulada', 16, 30.0, 480.0, 'Risco baixo/moderado: melhor caimento no acesso a Marginal.')
    ) AS x(codigo, pavimentacao, estado, tipo, quantidade, capacidade_individual, capacidade_total, expectativa)
    LOOP
        SELECT id INTO target_id FROM trechos WHERE codigo = item.codigo;
        IF NOT EXISTS (SELECT 1 FROM condicoes_pista WHERE trecho_id = target_id) THEN
            INSERT INTO condicoes_pista (trecho_id, pavimentacao, estado_pavimento, observacoes)
            VALUES (target_id, item.pavimentacao, item.estado,
                    'Dados simulados fornecidos para teste; nao representam vistoria de campo. Expectativa declarada: ' || item.expectativa || ' Nao e uma regra nem resultado garantido pelo algoritmo atual.');
        END IF;
        IF NOT EXISTS (SELECT 1 FROM drenagem WHERE trecho_id = target_id) THEN
            INSERT INTO drenagem (trecho_id, tipo, quantidade, capacidade_individual, capacidade_total, observacoes)
            VALUES (target_id, item.tipo, item.quantidade, item.capacidade_individual, item.capacidade_total,
                    'Capacidade simulada fornecida para teste; coeficiente de escoamento 0.90 assumido somente para teste.');
        END IF;
    END LOOP;
END $$;

INSERT INTO fontes_dados (nome, tipo, descricao, ativa)
VALUES ('Cemaden', 'meteorologica', 'Fonte candidata; associacoes abaixo sao dados de teste.', TRUE)
ON CONFLICT (nome) DO NOTHING;

INSERT INTO estacoes_meteorologicas (codigo_externo, fonte_id, nome, ativa, origem_dados, observacoes)
SELECT x.codigo, f.id, x.nome, TRUE, 'mock', x.observacoes
FROM (VALUES
    ('355030885A', 'Vila Maria / Parque Novo Mundo', 'Cobertura de teste informada para os km 225-228; coordenadas nao fornecidas.'),
    ('355030843A', 'Santana / Carandiru', 'Cobertura de teste informada para os km 228-230; coordenadas nao fornecidas.')
) AS x(codigo, nome, observacoes)
JOIN fontes_dados f ON f.nome = 'Cemaden'
ON CONFLICT (fonte_id, codigo_externo) DO NOTHING;

INSERT INTO trechos_estacoes (trecho_id, estacao_id, status_associacao, justificativa)
SELECT t.id, e.id, 'pendente_validacao',
       'Associacao de teste baseada na cobertura por km informada; validar coordenadas e representatividade antes de aceitar dados reais.'
FROM trechos t
JOIN estacoes_meteorologicas e ON
    (e.codigo_externo = '355030885A' AND t.codigo IN ('T-225', 'T-226', 'T-227')) OR
    (e.codigo_externo = '355030843A' AND t.codigo IN ('T-228', 'T-229'))
ON CONFLICT (trecho_id, estacao_id) DO NOTHING;

COMMIT;
