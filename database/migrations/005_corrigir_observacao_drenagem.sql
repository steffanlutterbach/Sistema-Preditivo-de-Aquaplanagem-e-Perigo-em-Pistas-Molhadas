-- Migração 005: padronização da coluna de observação da drenagem.

ALTER TABLE drenagem
ADD COLUMN IF NOT EXISTS observacao TEXT;

-- Preserva observações existentes na coluna antiga, se ela existir.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'drenagem'
          AND column_name = 'observacoes'
    ) THEN
        EXECUTE '
            UPDATE drenagem
            SET observacao = COALESCE(observacao, observacoes)
            WHERE observacoes IS NOT NULL
        ';
    END IF;
END $$;