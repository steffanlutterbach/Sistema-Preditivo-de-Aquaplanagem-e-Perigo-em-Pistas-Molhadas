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
psql -U aquasafe -d aquasafe -f database/migrations/004_seed_br116_via_dutra_mock.sql
psql -U aquasafe -d aquasafe -f database/migrations/005_update_via_dutra_test_geometry.sql
psql -U aquasafe -d aquasafe -f database/migrations/006_update_via_dutra_candidate_geometries.sql
psql -U aquasafe -d aquasafe -f database/migrations/007_update_br116_osm_geometries.sql
```

O usuario que executa a primeira migration precisa poder habilitar a extensao PostGIS. Execute migrations uma vez, na ordem. A migration 003 insere os cinco segmentos demonstrativos km 264-269; as migrations 004-006 adicionam e atualizam os cinco segmentos de teste Via Dutra km 225-230 e suas duas estacoes Cemaden. A migration 007 atualiza as geometrias dos dois grupos para seguir linhas conectadas da BR-116 no OpenStreetMap e corta cada trecho em 1.000 m. No grupo km 264-269, a fonte nao tem marcos oficiais que confirmem a quilometragem; os pontos foram alinhados ao corredor aproximado e permanecem marcados como nao validados. Geometrias de teste nao significam que o Cemaden foi consultado. `database/seeds/rodovias.sql` e `trechos.sql` sao seeds antigos e nao sao necessarios para esses cenarios.

As migrations 003 e 004 usam conflitos/verificacoes; migrations 005-007 atualizam os mesmos trechos de forma repetivel.

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

Os parametros hidrologicos continuam sendo os dados de teste fornecidos. As geometrias dos dois grupos foram alinhadas ao traçado conectado da BR-116 no OpenStreetMap, com atribuicao ODbL, e cortadas em segmentos de 1.000 m; nao foram levantamentos topograficos. No grupo km 264-269, a quilometragem e aproximada porque nao foram localizados marcos oficiais para ancorar os kms. Todas ficam com `geometria_validada=false`: aparecem no mapa mock, mas o monitoramento em modo real nao deve usa-las ate validacao espacial. As coordenadas das estacoes nao foram informadas e nao ha feed ao vivo do Cemaden. O segundo valor da coluna "Largura / L" foi interpretado como comprimento do caminho de escoamento para WD. O DNIT IPR-715 foi informado como referencia para coeficientes em asfalto, e Gallaway (1979) / DNIT como referencia de WD. A pontuacao atual nao utiliza WD. O comportamento esperado foi guardado como anotacao de teste, nao como regra nem garantia do algoritmo.
