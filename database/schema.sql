CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE rodovias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    descricao TEXT,
    CONSTRAINT uq_rodovias_nome_estado UNIQUE (nome, estado)
);

CREATE TABLE trechos (
    id SERIAL PRIMARY KEY,
    rodovia_id INTEGER NOT NULL REFERENCES rodovias(id) ON DELETE RESTRICT,
    km_inicial DECIMAL(10, 2),
    km_final DECIMAL(10, 2),
    comprimento DECIMAL(10, 2),
    largura DECIMAL(10, 2),
    area_contribuicao_m2 DECIMAL(14, 3),
    coeficiente_escoamento DECIMAL(4, 3),
    inclinacao DECIMAL(6, 3),
    geometria GEOMETRY(LineString, 4326),
    CONSTRAINT chk_trechos_km_intervalo CHECK (
        km_final IS NULL OR km_inicial IS NULL OR km_final >= km_inicial
    ),
    CONSTRAINT chk_trechos_dimensoes CHECK (
        (comprimento IS NULL OR comprimento > 0)
        AND (largura IS NULL OR largura > 0)
        AND (area_contribuicao_m2 IS NULL OR area_contribuicao_m2 > 0)
    ),
    CONSTRAINT chk_trechos_coef_escoamento CHECK (
        coeficiente_escoamento IS NULL
        OR (coeficiente_escoamento >= 0 AND coeficiente_escoamento <= 1)
    )
);

CREATE TABLE condicoes_pista (
    id SERIAL PRIMARY KEY,
    trecho_id INTEGER NOT NULL REFERENCES trechos(id) ON DELETE CASCADE,
    pavimentacao VARCHAR(50),
    estado_pavimento VARCHAR(30),
    observacoes TEXT,
    data_inspecao TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fontes_dados (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(50),
    descricao TEXT,
    ativa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dados_meteorologicos (
    id SERIAL PRIMARY KEY,
    trecho_id INTEGER NOT NULL REFERENCES trechos(id) ON DELETE CASCADE,
    fonte_id INTEGER REFERENCES fontes_dados(id) ON DELETE SET NULL,
    precipitacao DECIMAL(10, 3),
    intensidade_chuva DECIMAL(10, 3),
    data_hora TIMESTAMPTZ NOT NULL,
    CONSTRAINT chk_meteorologia_precipitacao CHECK (
        precipitacao IS NULL OR precipitacao >= 0
    ),
    CONSTRAINT chk_meteorologia_intensidade CHECK (
        intensidade_chuva IS NULL OR intensidade_chuva >= 0
    ),
    CONSTRAINT uq_meteorologia_trecho_fonte_data UNIQUE (trecho_id, fonte_id, data_hora)
);

CREATE TABLE drenagem (
    id SERIAL PRIMARY KEY,
    trecho_id INTEGER NOT NULL REFERENCES trechos(id) ON DELETE CASCADE,
    tipo VARCHAR(50),
    quantidade INTEGER NOT NULL DEFAULT 1,
    capacidade_individual DECIMAL(12, 3),
    capacidade_total DECIMAL(12, 3),
    CONSTRAINT chk_drenagem_quantidade CHECK (quantidade > 0),
    CONSTRAINT chk_drenagem_capacidades CHECK (
        (capacidade_individual IS NULL OR capacidade_individual >= 0)
        AND (capacidade_total IS NULL OR capacidade_total >= 0)
    )
);

CREATE TABLE analises_risco (
    id SERIAL PRIMARY KEY,
    trecho_id INTEGER NOT NULL REFERENCES trechos(id) ON DELETE CASCADE,
    dados_clima_id INTEGER NOT NULL REFERENCES dados_meteorologicos(id) ON DELETE RESTRICT,
    vazao_estimada DECIMAL(12, 3),
    volume_acumulado DECIMAL(14, 3),
    pontuacao_risco DECIMAL(5, 2),
    nivel_risco VARCHAR(20) NOT NULL,
    data_analise TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_analises_nivel_risco CHECK (
        nivel_risco IN ('baixo', 'moderado', 'alto')
    ),
    CONSTRAINT chk_analises_valores CHECK (
        (vazao_estimada IS NULL OR vazao_estimada >= 0)
        AND (volume_acumulado IS NULL OR volume_acumulado >= 0)
        AND (pontuacao_risco IS NULL OR (pontuacao_risco >= 0 AND pontuacao_risco <= 100))
    )
);

CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    analise_id INTEGER NOT NULL REFERENCES analises_risco(id) ON DELETE CASCADE,
    nivel VARCHAR(20) NOT NULL,
    mensagem TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    data_hora TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_alertas_nivel CHECK (nivel IN ('baixo', 'moderado', 'alto')),
    CONSTRAINT chk_alertas_status CHECK (status IN ('ativo', 'resolvido', 'expirado'))
);

CREATE INDEX idx_trechos_rodovia ON trechos (rodovia_id);
CREATE INDEX idx_trechos_geometria ON trechos USING GIST (geometria);
CREATE INDEX idx_condicoes_pista_trecho_data ON condicoes_pista (trecho_id, data_inspecao DESC);
CREATE INDEX idx_meteorologia_trecho_data ON dados_meteorologicos (trecho_id, data_hora DESC);
CREATE INDEX idx_drenagem_trecho ON drenagem (trecho_id);
CREATE INDEX idx_analises_trecho_data ON analises_risco (trecho_id, data_analise DESC);
CREATE INDEX idx_analises_clima ON analises_risco (dados_clima_id);
CREATE INDEX idx_alertas_analise ON alertas (analise_id);
CREATE INDEX idx_alertas_status_data ON alertas (status, data_hora DESC);
