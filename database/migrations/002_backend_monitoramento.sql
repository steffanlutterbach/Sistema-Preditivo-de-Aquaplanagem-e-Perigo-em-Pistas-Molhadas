-- Migração incremental e compatível com o schema inicial do AquaSafe.
-- Execute conectado ao banco existente: psql -d aquasafe -f 002_backend_monitoramento.sql

ALTER TABLE trechos ADD COLUMN IF NOT EXISTS codigo VARCHAR(40);
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS inclinacao_unidade VARCHAR(10) NOT NULL DEFAULT '%';
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS mtd_mm DECIMAL(8, 3);
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS caminho_escoamento_m DECIMAL(10, 3);
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS declividade_caminho_pct DECIMAL(8, 4);
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS geometria_validada BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS origem_dados VARCHAR(50) NOT NULL DEFAULT 'desconhecido';
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS estado_inclinacao VARCHAR(100);
ALTER TABLE trechos ADD COLUMN IF NOT EXISTS origem_geometria VARCHAR(100);
ALTER TABLE trechos ADD CONSTRAINT chk_trechos_mtd CHECK (mtd_mm IS NULL OR mtd_mm > 0);
ALTER TABLE trechos ADD CONSTRAINT chk_trechos_caminho CHECK (caminho_escoamento_m IS NULL OR caminho_escoamento_m > 0);
CREATE UNIQUE INDEX IF NOT EXISTS uq_trechos_codigo ON trechos (codigo) WHERE codigo IS NOT NULL;

CREATE TABLE IF NOT EXISTS estacoes_meteorologicas (
    id SERIAL PRIMARY KEY,
    codigo_externo VARCHAR(100),
    fonte_id INTEGER REFERENCES fontes_dados(id) ON DELETE SET NULL,
    nome VARCHAR(150) NOT NULL,
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    geometria GEOMETRY(Point, 4326),
    ativa BOOLEAN NOT NULL DEFAULT TRUE,
    origem_dados VARCHAR(20) NOT NULL DEFAULT 'real' CHECK (origem_dados IN ('real', 'mock')),
    observacoes TEXT,
    CONSTRAINT uq_estacao_fonte_codigo UNIQUE (fonte_id, codigo_externo)
);
CREATE INDEX IF NOT EXISTS idx_estacoes_geometria ON estacoes_meteorologicas USING GIST (geometria);

ALTER TABLE drenagem ADD COLUMN IF NOT EXISTS observacoes TEXT;

CREATE TABLE IF NOT EXISTS trechos_estacoes (
    trecho_id INTEGER NOT NULL REFERENCES trechos(id) ON DELETE CASCADE,
    estacao_id INTEGER NOT NULL REFERENCES estacoes_meteorologicas(id) ON DELETE CASCADE,
    status_associacao VARCHAR(30) NOT NULL DEFAULT 'pendente_validacao',
    distancia_km DECIMAL(8, 3),
    justificativa TEXT,
    PRIMARY KEY (trecho_id, estacao_id),
    CONSTRAINT chk_associacao_status CHECK (status_associacao IN ('validada', 'candidata', 'pendente_validacao', 'inativa'))
);

ALTER TABLE dados_meteorologicos ADD COLUMN IF NOT EXISTS estacao_id INTEGER REFERENCES estacoes_meteorologicas(id) ON DELETE SET NULL;
ALTER TABLE dados_meteorologicos ADD COLUMN IF NOT EXISTS modo_dados VARCHAR(20) NOT NULL DEFAULT 'desconhecido';
ALTER TABLE dados_meteorologicos ADD COLUMN IF NOT EXISTS identificador_externo VARCHAR(150);
ALTER TABLE dados_meteorologicos ADD CONSTRAINT chk_meteorologia_modo CHECK (modo_dados IN ('real', 'mock', 'desconhecido'));
CREATE UNIQUE INDEX IF NOT EXISTS uq_meteorologia_externo ON dados_meteorologicos (fonte_id, identificador_externo) WHERE identificador_externo IS NOT NULL;

ALTER TABLE analises_risco ALTER COLUMN nivel_risco DROP NOT NULL;
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS status_analise VARCHAR(30) NOT NULL DEFAULT 'concluida';
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS dados_utilizados JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS versao_algoritmo VARCHAR(40) NOT NULL DEFAULT 'risk-v1-experimental';
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS origem_dados VARCHAR(20) NOT NULL DEFAULT 'desconhecido';
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS dados_ausentes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[];
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS dados_desatualizados BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE analises_risco ADD COLUMN IF NOT EXISTS wd_mm DECIMAL(10, 4);
ALTER TABLE analises_risco DROP CONSTRAINT IF EXISTS chk_analises_nivel_risco;
ALTER TABLE analises_risco ADD CONSTRAINT chk_analises_nivel_risco CHECK (nivel_risco IS NULL OR nivel_risco IN ('baixo', 'moderado', 'alto'));
ALTER TABLE analises_risco ADD CONSTRAINT chk_analises_status CHECK (status_analise IN ('concluida', 'dados_insuficientes', 'dados_desatualizados'));

ALTER TABLE alertas ADD COLUMN IF NOT EXISTS validade TIMESTAMPTZ;
ALTER TABLE alertas ADD COLUMN IF NOT EXISTS chave_deduplicacao VARCHAR(120);
CREATE UNIQUE INDEX IF NOT EXISTS uq_alerta_ativo_deduplicacao ON alertas (chave_deduplicacao)
    WHERE status = 'ativo' AND chave_deduplicacao IS NOT NULL;
