# Documentação técnica — AquaSafe V2

## 1. Contexto e objetivo
A aquaplanagem envolve perda de contato pneu–pavimento pela presença de água. O projeto investiga como combinar dados meteorológicos e características rodoviárias para comunicar risco experimental. O objetivo do MVP é demonstrar a cadeia cadastro → medição → análise → alerta → visualização, não determinar uma velocidade segura ou prever acidentes.

## 2. Escopo e atores
Motorista demonstrativo: consulta mapa, risco e simula posição/sentido. Operador/testador: registra medições, configura trechos, associa estações e executa cenários via Swagger. Desenvolvedor: mantém código, testes, banco e documentação. Não existe autenticação individual por papéis; a API usa chave compartilhada quando configurada.

## 3. Dados de demonstração
| Região | IDs | Quilometragem cadastrada | Drenagem (L/s por ID) |
|---|---|---|---|
| Régis Bittencourt | 1–5 | 264–269 | 600, 400, 180, 504, 330 |
| Via Dutra | 6–10 | 225–230 | 420, 300, 200, 350, 480 |

Cada segmento tem comprimento cadastrado de 1.000 m. Geometrias LineString derivadas de traçados OSM, ainda sem validação de campo. Parâmetros de pavimento, largura, coeficiente, MTD e drenagem são dados de teste, não medições oficiais. Cinco estações cadastradas, três pendentes e duas marcadas validadas apenas em mock. Cenários de chuva: 5, 20, 35 mm/h. Arquivos fonte em `mock_data/`.

## 4. Motor de cálculo
Implementação: `backend/app/services/calculo_vazao.py` e `classificacao_risco.py`.

- Vazão estimada Q = C × i × A / 3600, em L/s; C é coeficiente adimensional entre 0 e 1, i em mm/h e A em m². A divisão converte horas em segundos; 1 mm sobre 1 m² equivale a 1 L.
- Volume V = P × A × C, em litros, com P em mm. Trata-se de volume de escoamento estimado, não volume necessariamente retido na pista.
- Drenagem suficiente quando Q ≤ capacidade total cadastrada. Sem capacidade, a classificação fica indisponível.
- Lâmina WD = max(0, 0,01485 × MTD^0,11 × L^0,43 × i^0,59 / S^0,42 − MTD), com MTD em mm, L em m, S = declividade percentual/100. Estimativa condicional; exige declividade específica do caminho de escoamento, não substituída automaticamente pela inclinação longitudinal. Ausência de parâmetro retorna `wd_mm:null` e lista de ausências. A origem bibliográfica da expressão deve ser confirmada antes de alegar validade física.
- Pontuação: min(100, 2i + fator de pavimento + penalidade de drenagem). Fatores: bom 0, regular 15, ruim/irregular 30. Penalidade 15 quando drenagem insuficiente. Baixo <35; moderado ≥35 e <70; alto ≥70. WD não entra na pontuação atual.

Exemplo: segmento 1, C=0,85, i=5, A=10.500, P=5: Q=12,396 L/s, V=44.625 L, pontuação 10. A capacidade 600 L/s é superior à vazão. O risco experimental é baixo, sem alerta. Isso não garante pista segura.

## 5. Regras de negócio
- Dados necessários para classificação: intensidade, precipitação, pavimento reconhecido, área, coeficiente, capacidade de drenagem e origem mock/real. Medição vencida ou dados insuficientes impedem classificação; cálculos parciais podem existir.
- `classificacao_confiavel` permanece falso. `classificacao_disponivel` indica apenas existência de nível calculado.
- Simulação usa chuva do cenário e parâmetros do trecho cadastrado; capacidade de drenagem do cenário é descritiva e não substitui a cadastrada. Em mock persiste em memória; em real não grava a simulação no banco operacional.
- Alertas moderados/altos têm validade padrão de 30 min; deduplicação por trecho e chave de notificação; queda de risco resolve alerta. Atualidade padrão da meteorologia: 60 min.
- Localização: correspondência por proximidade a linhas, tolerância padrão 350 m, sentido crescente/decrescente, próximos trechos da mesma rodovia até 5 km. Resposta declara que localização não é armazenada. Geometria mock não serve para navegação. Distância longitudinal possui ressalva registrada.
- Dados externos: fontes INMET/CEMADEN, precipitação ≥0 e <9999, horário normalizado em UTC; intensidade permanece nula quando não fornecida/calculável. Estação informada deve ter associação válida. Duplicidade por trecho, fonte e horário retorna 409.

## 6. Rastreabilidade e limitações
A análise registra parâmetros usados, versão `risk-v1-experimental`, origem e campos ausentes. A rota de simulação ainda deixa alguns metadados como desconhecidos, embora a rota de análise explícita os propague. Ver [validação](VALIDACAO.md) e [manutenção](MANUTENCAO.md). O modelo não considera diretamente velocidade, pneus, pressão, aderência ou dinâmica veicular; não foi calibrado com dados de acidentes ou medições físicas. Nenhuma alegação de desempenho operacional é sustentada pelos testes mock.
