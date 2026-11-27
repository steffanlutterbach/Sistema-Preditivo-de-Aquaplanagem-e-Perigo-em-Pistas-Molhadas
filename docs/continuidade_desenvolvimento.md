# Continuidade do desenvolvimento AquaSafe

Este documento registra o ponto de parada para que outra pessoa possa continuar o trabalho sem presumir que serviços ou banco de dados já foram iniciados.

## Situação atual

- O projeto contém um backend FastAPI e um frontend React com mapa Leaflet. A estrutura de pastas existente deve ser mantida.
- O modo padrão do backend é `DATA_MODE=mock`. Nesse modo, os dados de referência vêm de `mock_data/`; não é necessário PostgreSQL para iniciar a aplicação.
- Os arquivos JSON incluem dez segmentos de teste em duas regiões da BR-116: km 264-269 e km 225-230. As geometrias foram atualizadas para acompanhar vias contínuas do OpenStreetMap e cortadas em cinco segmentos de aproximadamente 1 km por região.
- A geometria km 264-269 tem quilometragem aproximada: não foram confirmados marcos oficiais para ancorar cada km. Todas as geometrias estão com `geometria_validada=false`. São dados para demonstração/teste, não devem ser usados para orientar tráfego ou ativar o modo real.
- A origem OpenStreetMap e a atribuição ODbL estão registradas nos dados. Para redistribuir mapas ou dados derivados, mantenha a atribuição exigida pela licença.
- O cálculo de risco e os endpoints já existem. O WD é complementar/condicional quando os dados necessários estão disponíveis; a inclinação da via é representada em porcentagem.
- Não há coleta automática ativa do INMET ou Cemaden nesta etapa. As integrações são candidatas/stubs; medições de teste podem ser enviadas pela API. Consulte `docs/integracoes.md` e `docs/endpoints.md`.
- Nenhum banco foi iniciado nesta etapa e as migrations não foram aplicadas. A migration `007_update_br116_osm_geometries.sql` apenas deixa preparada a atualização PostGIS. Em mock, ela não é usada.
- Os testes existentes foram ajustados para as novas geometrias. Nesta etapa, foi conferido que o JSON é válido, que os cinco segmentos de cada região se conectam e que medem aproximadamente 1 km. A suíte automatizada e a aplicação visual não foram executadas após essas alterações.

## Como retomar em modo mock

Use dois terminais, a partir da raiz do repositório.

Terminal 1 — backend:

```powershell
cd backend
$env:DATA_MODE = "mock"
python -m uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para explorar a API e `http://127.0.0.1:8000/health` para conferir seu estado.

Terminal 2 — frontend:

```powershell
cd frontend
npm run dev
```

Abra a URL local impressa pelo Vite. Verifique se o frontend aponta para `http://127.0.0.1:8000`, se as duas regiões aparecem no mapa e se selecionar um trecho mostra os dados esperados. O modo mock perde medições, análises, alertas e alterações feitas via API quando o backend reinicia.

Se `npm` não for reconhecido, Node.js/npm não estão disponíveis no terminal atual. Instale/ative Node.js e abra um novo terminal antes de repetir o comando.

## Próximos passos recomendados

1. **Revisar as alterações locais** e confirmar com a equipe quais arquivos cada pessoa está editando antes de integrar ou fazer commit. Não sobrescrever trabalho local de outra pessoa.
2. **Rodar a aplicação e inspecionar o mapa** nas duas regiões. Confirmar zoom, cores, seleção dos segmentos e requisições do frontend ao backend.
3. **Validar a localização e a quilometragem com uma fonte rodoviária oficial ou inspeção manual no mapa.** O km 264-269 é aproximado; o alinhamento ao OSM confirma o traçado da via, mas não confirma os rótulos quilométricos. No km 225-230, também conferir se os marcos e o sentido correspondem à referência do projeto.
4. **Executar a suíte do backend** após revisar os dados e corrigir qualquer divergência. Os testes ficam em `backend/tests/`.
5. **Definir com a equipe se e quando será usado PostgreSQL/PostGIS.** Se a decisão for seguir com banco real, instalar/iniciar PostgreSQL com PostGIS, criar o banco, configurar `DATABASE_URL` e `AQUASAFE_API_KEY`, e então aplicar as migrations em ordem conforme `docs/banco_de_dados.md`. A migration 007 precisa ser aplicada depois da 006. Não definir `DATA_MODE=real` sem cumprir esses passos.
6. **Retomar as integrações meteorológicas separadamente.** Antes de ativar um provedor, confirmar cobertura, formato, frequência, atribuição/licença e política de operação. Até lá, usar envio manual ou dados mock, sem apresentar esses dados como observações ao vivo.
7. **Revisar a lógica de risco e seus limites** com critérios técnicos documentados. Os valores de teste e os resultados simulados não são limites de segurança validados.

## Arquivos úteis

- Dados de referência: `mock_data/trechos.json`, `mock_data/rodovias.json`, `mock_data/estacoes.json`.
- API e execução: `backend/app/main.py`, `docs/endpoints.md`.
- Lógica de risco: `backend/app/services/`.
- Configuração e repositórios: `backend/app/core/config.py`, `backend/app/repositories/`.
- Integrações candidatas: `backend/app/integrations/`, `docs/integracoes.md`.
- Banco e migrations: `database/migrations/`, `docs/banco_de_dados.md`.
- Frontend: `frontend/README.md`.

## Observação sobre o estado do Git

As alterações desta etapa ainda não foram commitadas. Antes de criar um commit, revisar `git status` e `git diff`, pois o diretório pode conter trabalho anterior da equipe além da atualização das geometrias e desta documentação.
