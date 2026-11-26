# Banco de dados

O backend usa PostgreSQL/PostGIS em `DATA_MODE=real` e arquivos JSON mais estado em memória em `DATA_MODE=mock`. No modo mock, medições, análises, alertas e alterações via API são perdidos ao reiniciar o processo. Nenhuma migration é executada automaticamente pela API.

## Criar o banco

Os arquivos SQL criam a estrutura **dentro de um banco já criado**. Eles não instalam o PostgreSQL/PostGIS nem criam o banco lógico. Em uma instalação local com `psql` e PostGIS disponíveis, conecte como administrador e crie role e banco (substitua a senha):

```sql
CREATE ROLE aquasafe LOGIN PASSWORD 'defina-uma-senha-forte';
CREATE DATABASE aquasafe OWNER aquasafe;
```

Depois, a partir da raiz do repositório, aplique em ordem com `psql`:

```powershell
psql -U aquasafe -d aquasafe -f database/migrations/001_initial_schema.sql
psql -U aquasafe -d aquasafe -f database/migrations/002_backend_monitoramento.sql
psql -U aquasafe -d aquasafe -f database/migrations/003_seed_br116_mock.sql
```

O usuário que executa a primeira migration precisa poder habilitar a extensão PostGIS. Execute migrations uma vez, na ordem. A migration 003 insere os cinco segmentos e as estações candidatas como dados mock; não valida geometrias ou associações. `database/seeds/rodovias.sql` e `trechos.sql` são seeds antigos da rodovia demonstrativa e não são necessários para o cenário BR-116.

As migrations são incrementais e não removem tabelas nem registros. A migration 002 acrescenta identificadores, dados opcionais para WD, estações e associações, origem/atualidade da meteorologia, rastreabilidade das análises e validade/deduplicação de alertas. Registros anteriores, cuja origem não pode ser inferida, são marcados `desconhecido`; não geram classificação até receberem medições com proveniência. A migration 003 usa `ON CONFLICT DO NOTHING`/verificações para evitar duplicar segmentos, fontes, estações e associações sem sobrescrever registros existentes.

## Executar a API

A partir da pasta `backend`:

```powershell
# Mock local
$env:DATA_MODE = "mock"
uvicorn app.main:app --reload

# Banco real já migrado
$env:DATA_MODE = "real"
$env:DATABASE_URL = "postgresql://aquasafe:SENHA@localhost:5432/aquasafe"
$env:AQUASAFE_API_KEY = "CHAVE-FORTE"
uvicorn app.main:app --reload
```

`DATA_MODE=real` persiste dados no PostgreSQL e exige a chave de API. Ainda não ativa coleta automática em INMET/Cemaden: os arquivos dessas integrações continuam candidatos sem adaptadores de consulta implementados. Medições reais podem ser recebidas pelo endpoint documentado de meteorologia.

Inclinação é armazenada na coluna existente `trechos.inclinacao`, padronizada em `%` pela migration. Para WD, a declividade específica do caminho (`declividade_caminho_pct`) pode ser informada quando disponível; na ausência dela, o backend usa a inclinação `S` fornecida para o trecho, também em porcentagem.
