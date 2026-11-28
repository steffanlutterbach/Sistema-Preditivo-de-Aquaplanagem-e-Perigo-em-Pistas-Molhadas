-- Migração 004: rastreabilidade das condições de pista e drenagem.
-- Registros existentes permanecem como desconhecidos até validação.

ALTER TABLE condicoes_pista
ADD COLUMN IF NOT EXISTS origem_dados VARCHAR(20) NOT NULL DEFAULT 'desconhecido';

ALTER TABLE drenagem
ADD COLUMN IF NOT EXISTS origem_dados VARCHAR(20) NOT NULL DEFAULT 'desconhecido';

ALTER TABLE condicoes_pista
DROP CONSTRAINT IF EXISTS chk_condicoes_pista_origem;

ALTER TABLE condicoes_pista
ADD CONSTRAINT chk_condicoes_pista_origem
CHECK (origem_dados IN ('real', 'mock', 'manual', 'desconhecido'));

ALTER TABLE drenagem
DROP CONSTRAINT IF EXISTS chk_drenagem_origem;

ALTER TABLE drenagem
ADD CONSTRAINT chk_drenagem_origem
CHECK (origem_dados IN ('real', 'mock', 'manual', 'desconhecido'));
