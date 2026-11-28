# API REST — referência de endpoints

Base local: `http://127.0.0.1:8000`. Swagger `/docs`, especificação `/openapi.json`. JSON e header `Content-Type: application/json` para corpos. Header `X-API-Key` quando configurado; obrigatório no modo real. Os esquemas Pydantic em `backend/app/schemas/__init__.py` são a referência executável.

| Método | Rota | Entrada / finalidade | Sucesso |
|---|---|---|---|
| GET | /health | Saúde e modo | 200 |
| GET | /rodovias | Lista de rodovias | 200 |
| GET | /trechos | rodovia_id opcional | 200 |
| POST | /trechos | Cadastro TrechoInput | 201 |
| GET | /trechos/{trecho_id} | Detalhes | 200 |
| PATCH | /trechos/{trecho_id} | Atualização parcial | 200 |
| GET | /trechos/{trecho_id}/estacoes | Estações associadas | 200 |
| GET | /trechos/{trecho_id}/risco | Risco atual | 200 |
| GET | /meteorologia | trecho_id opcional | 200 |
| POST | /meteorologia | Medição manual | 200 |
| POST | /meteorologia/externa | Normalização de observação | 200 |
| GET | /meteorologia/estacoes | trecho_id opcional | 200 |
| POST | /meteorologia/estacoes | Cadastro de estação | 201 |
| PUT | /meteorologia/estacoes/{estacao_id}/trechos/{trecho_id} | Associação | 200 |
| POST | /analises | Executar análise | 200 |
| GET | /analises | Histórico, trecho_id opcional | 200 |
| GET | /alertas | trecho_id opcional; historico booleano | 200 |
| GET | /mapa/riscos | GeoJSON FeatureCollection | 200 |
| GET | /simulacoes/cenarios | Cenários locais | 200 |
| POST | /simulacoes | cenario_id, trecho_id | 200 |
| POST | /monitoramento/localizacao | latitude, longitude, sentido opcional | 200 |

## Exemplos de corpo JSON
Simulação:
```json
{"cenario_id": 2, "trecho_id": 2}
```
Medição direta (timestamp ilustrativo, atualizar para testar atualidade):
```json
{"trecho_id": 1, "fonte": "MOCK_MANUAL", "precipitacao_mm": 20, "intensidade_mm_h": 20, "data_hora": "2026-11-28T06:15:00Z"}
```
Medição externa simulada:
```json
{"fonte": "INMET", "trecho_id": 1, "precipitacao_mm": 12.5, "data_hora": "2026-11-28T06:15:00Z"}
```
Análise com medição recente já cadastrada:
```json
{"trecho_id": 1}
```
Monitoramento:
```json
{"latitude": -23.5946132, "longitude": -46.7376195, "sentido": "crescente"}
```
Atualização de declividade (somente valor artificial em mock de teste):
```json
{"declividade_caminho_percentual": 1.5}
```
Cadastro de estação: `codigo_externo`, `fonte`, `nome` obrigatórios; latitude/longitude, origem e observações opcionais. Associação: `status_associacao` (validada, candidata, pendente_validacao, inativa), distância e justificativa opcionais. Não marcar associação real como validada sem evidência de campo.

Cadastro de trecho exige código, rodovia_id, km_inicial e km_final; parâmetros opcionais incluem comprimento, largura, coeficiente [0,1], inclinação percentual, pavimento, MTD, caminho, declividade específica, drenagem e geometria com origem. PATCH permite atualização parcial. Consulte Swagger para os tipos completos.

## Respostas e erros
200/201 sucesso; 404 recurso inexistente; 409 conflito de medição ou cadastro; 422 validação de corpo ou associação; 503 indisponibilidade de banco tratada; autenticação depende da configuração. Os códigos 404 e 409 observados ainda não estão explicitamente declarados em certas operações OpenAPI. Os resultados de análise incluem dados_utilizados, pontuacao_risco, nivel_risco, status_analise, wd_mm, wd_status, dados_ausentes e alerta. `null` representa indisponibilidade, nunca risco zero automaticamente.
