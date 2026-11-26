# Contratos da API AquaSafe

Base local: `http://127.0.0.1:8000`. A documentação interativa do FastAPI fica em `/docs`.

## Segmentos

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/rodovias` | Lista rodovias |
| GET | `/trechos?rodovia_id=1` | Lista ou filtra segmentos |
| POST | `/trechos` | Cadastra um segmento |
| GET | `/trechos/{id}` | Consulta um segmento |
| PATCH | `/trechos/{id}` | Atualiza os campos enviados |
| GET | `/trechos/{id}/risco` | Retorna a análise mais recente |
| GET | `/trechos/{id}/estacoes` | Lista estações associadas/candidatas |
| GET | `/mapa/riscos` | FeatureCollection GeoJSON com geometria e estado da análise |

Exemplo de cadastro:

```json
{
  "codigo": "BR116-269",
  "rodovia_id": 1,
  "km_inicial": 269,
  "km_final": 270,
  "comprimento_m": 1000,
  "largura_m": 10.5,
  "area_contribuicao_m2": 10500,
  "coeficiente_escoamento": 0.9,
  "inclinacao_percentual": 2.1,
  "estado_inclinacao": "longitudinal",
  "pavimentacao": "CAUQ",
  "estado_pavimento": "regular",
  "geometria": {"type": "LineString", "coordinates": [[-46.75, -23.60], [-46.76, -23.61]]},
  "geometria_validada": false,
  "origem_geometria": "simulada"
}
```

Inclinação cadastral é sempre percentual. Os dados fornecidos identificam esse valor como `S`; o cálculo WD usa `declividade_caminho_percentual` quando informado e, na ausência dele, usa `inclinacao_percentual` fornecida para o segmento. A origem de `S` usada é registrada na análise. Uma medição mais específica do caminho pode substituir a inclinação geral.

## Estações e meteorologia

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/meteorologia/estacoes?trecho_id=1` | Lista estações ou candidatas |
| POST | `/meteorologia/estacoes` | Cadastra estação |
| PUT | `/meteorologia/estacoes/{estacao_id}/trechos/{trecho_id}` | Registra/atualiza associação e seu estado de validação |
| POST | `/meteorologia` | Registra medição recebida |
| GET | `/meteorologia?trecho_id=1` | Consulta medições e indicador de atualidade |

Exemplo de medição:

```json
{
  "trecho_id": 3,
  "fonte": "MOCK_LOCAL",
  "precipitacao_mm": 35,
  "intensidade_mm_h": 35,
  "data_hora": "2026-11-26T12:00:00-03:00"
}
```

O modo de origem é definido pelo backend. Medições duplicadas para o mesmo segmento, fonte e instante retornam `409`. Associações de estação iniciam pendentes; uma medição que declare `estacao_id` só é aceita se a associação ao segmento estiver validada. A idade máxima por padrão é 60 minutos (`METEOROLOGY_STALE_MINUTES`). O modo `real` persiste medições recebidas; não consulta por conta própria INMET ou Cemaden.

## Análises de risco

| Método | Endpoint | Finalidade |
|---|---|---|
| POST | `/analises` | Analisa os dados informados ou a medição mais recente |
| GET | `/analises?trecho_id=3` | Consulta histórico de análises |

Exemplo:

```json
{
  "trecho_id": 3,
  "intensidade_mm_h": 35,
  "precipitacao_mm": 35,
  "data_hora": "2026-11-26T12:00:00-03:00"
}
```

O resultado inclui `status_analise`, `nivel_risco`, `classificacao_disponivel`, `classificacao_confiavel`, entradas utilizadas, versão do algoritmo, origem, dados ausentes/desatualizados, vazão, volume e WD quando calculável. A classificação fica indisponível quando a medição está vencida ou faltam intensidade, precipitação, origem conhecida (`mock`/`real`), estado do pavimento, área, coeficiente ou capacidade de drenagem. Registros que já estavam no banco antes da migration 002 ficam com origem `desconhecido` e não são classificados até serem recadastrados com proveniência. `classificacao_confiavel` permanece `false`: o motor é experimental.

Fórmulas do planejamento:

- Vazão: `Q = (C × i × A) / 3600`, em L/s.
- Volume: `V = P × A × C`, em litros.
- WD é complementar e só é calculada quando MTD, comprimento do caminho, intensidade e inclinação `S` estão presentes. A inclinação informada em `%` é convertida para razão `m/m` na fórmula. Os dados atuais fornecem esses parâmetros, então o WD pode ser calculado nos cenários mock. WD não participa da pontuação de risco; eventual resultado negativo da fórmula é limitado a zero, pois lâmina negativa não é fisicamente interpretável.

A pontuação atual é uma regra provisória do MVP: `min(100, 2 × intensidade + fator do pavimento + penalidade de drenagem insuficiente)`. Fatores: bom `0`, regular `15`, ruim/irregular `30`; drenagem insuficiente acrescenta `15`. Pontuações abaixo de `35` são baixo, `35–69` moderado, `70+` alto. Os exemplos de 5/20/35 mm/h foram usados para testar as três classes; esses valores não são limites de segurança validados. Não usar a saída para orientar a condução em rodovia real.

## Alertas e monitoramento por localização

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/alertas?trecho_id=3` | Lista alertas ativos |
| GET | `/alertas?trecho_id=3&historico=true` | Inclui histórico resolvido/expirado |
| POST | `/monitoramento/localizacao` | Correlaciona uma posição recebida a segmentos e riscos próximos |

Exemplo de posição:

```json
{"latitude": -23.601, "longitude": -46.744, "sentido": "crescente"}
```

A resposta contém segmento atual, segmentos seguintes, distância aproximada, níveis, alertas, validade e uma `chave_notificacao` estável para deduplicação no aplicativo. O sentido pode ser `crescente` ou `decrescente`; ausente, assume km crescente e marca `sentido_assumido: true`. A antecedência padrão é 5 km (`ALERT_LEAD_DISTANCE_METERS`) e a tolerância de correspondência é 350 m (`LOCATION_MATCH_TOLERANCE_METERS`). Distâncias ao longo do trajeto usam comprimentos cadastrados.

O endpoint não grava nem registra as coordenadas recebidas. Em modo mock, as geometrias são aproximadas, fornecidas para teste, e a resposta identifica essa condição. Em modo real, apenas geometrias marcadas como validadas participam da correspondência. Coordenadas simuladas não devem ser usadas para navegação real.

Alertas moderados e altos duram 30 minutos por padrão (`ALERT_VALIDITY_MINUTES`). Um alerta ativo do mesmo segmento e nível é atualizado em vez de duplicado; mudança de nível resolve o anterior e gera uma nova chave de notificação. Risco baixo resolve alertas ativos do segmento.

## Simulações e saúde

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/simulacoes/cenarios` | Lista os três cenários mock |
| POST | `/simulacoes` | Executa cenário em um segmento |
| GET | `/health` | Verifica a API e, em modo real, a conexão ao banco |

Exemplo: `{"cenario_id": 3, "trecho_id": 3}`. Em modo real, a simulação é isolada e não persiste cenário, análise ou alerta no banco operacional.

## Segurança e erros

Quando `DATA_MODE=real`, `AQUASAFE_API_KEY` é obrigatória e as rotas exigem o header `X-API-Key`. Em `mock`, a chave é opcional para facilitar desenvolvimento local. É uma chave compartilhada de serviço, não identidade de usuário; localização não é armazenada e não há conta de usuário no backend atual.

O CORS permite por padrão `localhost:5173` e `127.0.0.1:5173`; ajuste `CORS_ORIGINS` para a origem web configurada pela equipe.

Para validar localmente, instale `backend/requirements.txt` e execute `python -m pytest -q` dentro de `backend/`.

- `200`: consulta ou processamento concluído.
- `201`: segmento/estação cadastrados.
- `401`: chave ausente ou inválida.
- `404`: rodovia, segmento, cenário ou estação não encontrado.
- `409`: duplicidade ou conflito.
- `422`: entrada inválida ou associação pendente.
- `503`: banco indisponível ou migration pendente.
