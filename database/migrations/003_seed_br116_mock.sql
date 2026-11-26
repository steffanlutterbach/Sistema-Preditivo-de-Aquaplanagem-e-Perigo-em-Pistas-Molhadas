-- Dados demonstrativos fornecidos para testes. Coordenadas aproximadas e
-- geometrias não validadas; nunca representam levantamento oficial.
BEGIN;

INSERT INTO rodovias (nome,estado,descricao)
VALUES ('BR-116 — Régis Bittencourt (segmentos demonstrativos)','SP',
        'Cadastro de teste AquaSafe; localização aproximada fornecida pelo usuário, pendente de validação oficial.')
ON CONFLICT (nome,estado) DO NOTHING;

WITH road AS (SELECT id FROM rodovias WHERE nome='BR-116 — Régis Bittencourt (segmentos demonstrativos)' AND estado='SP'),
seed(codigo,km_i,km_f,c,inc,inc_text,mtd,path,lat1,lon1,lat2,lon2) AS (VALUES
 ('BR116-264',264.0,265.0,0.850,3.500,'Descida moderada; dado simulado',0.800,10.8,-23.5935,-46.7340,-23.5968,-46.7385),
 ('BR116-265',265.0,266.0,0.900,1.500,'Trecho mais plano; dado simulado',0.550,11.2,-23.5968,-46.7385,-23.6001,-46.7432),
 ('BR116-266',266.0,267.0,0.950,0.800,'Baixada urbana; dado simulado',0.350,12.0,-23.6001,-46.7432,-23.6030,-46.7480),
 ('BR116-267',267.0,268.0,0.880,4.200,'Aclive; dado simulado',0.600,11.0,-23.6030,-46.7480,-23.6058,-46.7528),
 ('BR116-268',268.0,269.0,0.900,2.100,'Inclinação suave; dado simulado',0.500,11.5,-23.6058,-46.7528,-23.6085,-46.7575)
)
INSERT INTO trechos (codigo,rodovia_id,km_inicial,km_final,comprimento,largura,area_contribuicao_m2,
    coeficiente_escoamento,inclinacao,inclinacao_unidade,estado_inclinacao,mtd_mm,caminho_escoamento_m,
    geometria,geometria_validada,origem_dados,origem_geometria)
SELECT s.codigo,road.id,s.km_i,s.km_f,1000,10.5,10500,s.c,s.inc,'%',s.inc_text,s.mtd,s.path,
       ST_SetSRID(ST_MakeLine(ST_MakePoint(s.lon1,s.lat1),ST_MakePoint(s.lon2,s.lat2)),4326),FALSE,'mock'
       ,'Coordenadas aproximadas fornecidas para simulação; não validadas oficialmente.'
FROM seed s CROSS JOIN road
ON CONFLICT (codigo) WHERE codigo IS NOT NULL DO NOTHING;

DO $$
DECLARE item RECORD; target_id INTEGER;
BEGIN
  FOR item IN SELECT * FROM (VALUES
    ('BR116-264','CAUQ','bom','Boca de lobo simples',20,30.0,600.0),
    ('BR116-265','CAUQ','regular','Boca de lobo simples',16,25.0,400.0),
    ('BR116-266','CAUQ','irregular','Grelha de sarjeta / Boca de lobo',12,15.0,180.0),
    ('BR116-267','CAUQ','regular','Boca de lobo simples',18,28.0,504.0),
    ('BR116-268','CAUQ','regular','Boca de lobo simples',15,22.0,330.0)
  ) AS x(codigo,pavimento,estado,tipo,quantidade,cap_ind,cap_total)
  LOOP
    SELECT id INTO target_id FROM trechos WHERE codigo=item.codigo;
    IF NOT EXISTS (SELECT 1 FROM condicoes_pista WHERE trecho_id=target_id) THEN
      INSERT INTO condicoes_pista(trecho_id,pavimentacao,estado_pavimento,observacoes)
      VALUES(target_id,item.pavimento,item.estado,'Dado simulado fornecido para teste; requer vistoria para uso real.');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM drenagem WHERE trecho_id=target_id) THEN
      INSERT INTO drenagem(trecho_id,tipo,quantidade,capacidade_individual,capacidade_total)
      VALUES(target_id,item.tipo,item.quantidade,item.cap_ind,item.cap_total);
    END IF;
  END LOOP;
END $$;

UPDATE drenagem dr SET observacoes='Capacidade informada como parcialmente obstruída; não medida em campo.'
FROM trechos t WHERE t.id=dr.trecho_id AND t.codigo='BR116-266' AND dr.observacoes IS NULL AND t.origem_dados='mock';

INSERT INTO fontes_dados(nome,tipo,descricao,ativa)
VALUES ('INMET','meteorologica','Fonte candidata; nenhuma consulta externa configurada.',TRUE),
       ('Cemaden','meteorologica','Fonte candidata; estação e representatividade pendentes de validação.',TRUE)
ON CONFLICT (nome) DO NOTHING;

INSERT INTO estacoes_meteorologicas (codigo_externo,fonte_id,nome,ativa,origem_dados,observacoes)
SELECT x.codigo,f.id,x.nome,TRUE,'mock',x.observacao
FROM (VALUES
 ('CEMADEN-BUTANTA-CANDIDATA','Cemaden','Pluviômetros da Subprefeitura do Butantã / Vila Sônia','Candidata indicada pelo usuário; coordenadas, distância, cobertura e representatividade não verificadas.'),
 ('INMET-A701-CANDIDATA','INMET','Estação Automática São Paulo - Mirante de Santana (A701)','Candidata indicada pelo usuário; associação ao corredor não validada.'),
 ('INMET-A771-CANDIDATA','INMET','Estação Automática São Paulo - Interlagos (A771)','Candidata indicada pelo usuário; associação ao corredor não validada.')
) AS x(codigo,nome_fonte,nome,observacao)
JOIN fontes_dados f ON f.nome=x.nome_fonte
ON CONFLICT (fonte_id,codigo_externo) DO NOTHING;

INSERT INTO trechos_estacoes(trecho_id,estacao_id,status_associacao,justificativa)
SELECT t.id,e.id,'pendente_validacao','Associação de teste; verificar distância, cobertura e representatividade antes de usar dados.'
FROM trechos t CROSS JOIN estacoes_meteorologicas e
WHERE t.codigo LIKE 'BR116-%' AND e.codigo_externo IN
 ('CEMADEN-BUTANTA-CANDIDATA','INMET-A701-CANDIDATA','INMET-A771-CANDIDATA')
ON CONFLICT (trecho_id,estacao_id) DO NOTHING;

COMMIT;
