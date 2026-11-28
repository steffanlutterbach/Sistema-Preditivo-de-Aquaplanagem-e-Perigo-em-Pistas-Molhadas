# Relatório de validação funcional — AquaSafe

**API:** 0.2.0 | **Período:** 26–27/11/2026 | **Ambiente:** Windows, Python 3.12.3, pytest 8.4.2, FastAPI/Uvicorn, Swagger UI, modo mock.

## Escopo, método e critérios
Validação funcional do backend com dados simulados: inspeção de código, três execuções da suíte existente, correção de falhas, testes manuais positivos e negativos. Aprovação exige resposta HTTP e conteúdo esperados. Não constitui validação de segurança viária, cobertura integral, desempenho sob carga ou teste de banco real. Os resultados são históricos, obtidos no computador do responsável pelo projeto, e não reexecutados integralmente nesta consolidação.

## Evolução automatizada
| Rodada | Aprovados | Reprovados | Aprovação | Duração | Evidência |
|---|---:|---:|---:|---:|---|
| 1 | 8 | 17 | 32% | 1,37 s | [Log 1](resultado_testes.txt) |
| 2 | 24 | 1 | 96% | 2,04 s | [Log 2](resultado_testes_02.txt) |
| 3 | 25 | 0 | 100% | 0,99 s | [Log 3](resultado_testes_03.txt) |

Melhoria de 68 pontos percentuais. A lista completa de testes está no terceiro log; os arquivos foram convertidos de UTF-16 para UTF-8 para leitura no GitHub, sem alteração intencional do conteúdo textual.

## Não conformidades e ações corretivas
| ID | Falha | Ação | Verificação |
|---|---|---|---|
| NC-001 | 15 respostas 422 indevidas e 2 KeyError em testes HTTP | Inclusão de Content-Type application/json no auxiliar request de test_backend_mvp.py | 16 falhas eliminadas na segunda rodada |
| NC-002 | ValueError de medição duplicada em simulações consecutivas | Em main.py, reutilizar medição idêntica por fonte, instante, trecho e valores; conflito não idêntico retorna 409 | Teste antes reprovado e suíte aprovados na terceira rodada |
| NC-003 | Cópia ZIP atualizada contém indentação inválida na linha 99 de main.py | Ajustado o recuo de if DATA_MODE == "mock" de oito para quatro espaços, sem mudar a lógica | Compilação estática aprovada; reteste completo local pendente |

Não foi possível executar novamente a suíte nesta consolidação por ausência de psycopg no ambiente. Os 25 resultados positivos pertencem à execução anterior registrada, não a uma nova execução do ZIP corrigido. A hipótese de colisão temporal explica NC-002, mas não foi comprovada por instrumentação do relógio.

## Casos manuais e resultados
| ID | Requisição / entrada | Esperado | Observado | Resultado |
|---|---|---|---|---|
| VM-01 | GET /health | 200; ok, mock | 200; ok, mock, banco não utilizado | Aprovado |
| VM-02 | GET /trechos?rodovia_id=1 | 200; cinco registros | 200; IDs 1–5, km 264–269, JSON completo | Aprovado |
| VM-03 | GET /simulacoes/cenarios | 200; três cenários | 200; 5, 20 e 35 mm/h | Aprovado |
| VM-04 | POST /simulacoes; cenário 1, trecho 1 | 200; baixo, sem alerta | 200; baixo, 10 pontos, alerta nulo | Aprovado |
| VM-05 | POST /simulacoes; cenário 2, trecho 2 | 200; moderado, alerta | 200; moderado, 55 pontos, alerta 1 | Aprovado |
| VM-06 | POST /simulacoes; cenário 3, trecho 3 | 200; alto, alerta | 200; alto, 100 pontos, alerta 2 | Aprovado |
| VM-07 | GET /alertas?trecho_id=3&historico=false | 200; alerta ativo | 200; alerta 2, alto | Aprovado |
| VM-07B | Repetir cenário 3/trecho 3 e consultar alertas | Um alerta ativo, chave estável, validade renovada | 200; ID 2 e chave estáveis; validade renovada; análise original 5 | Aprovado com ressalva |
| VM-08 | POST /monitoramento/localizacao; latitude -23.59515, longitude -46.73625, crescente | 200; trecho 1 e alertas próximos | 200; trecho 1, quatro seguintes, dois alertas, armazenamento declarado falso | Aprovado |
| VM-09 | POST /monitoramento/localizacao; latitude 100, longitude 200 | 422; rejeitar ambos | 422; erros nos dois campos | Aprovado |
| VM-10 | GET /trechos/9999 | 404; trecho não encontrado | 404; mensagem correspondente | Aprovado |

Dez casos principais aprovados; um complementar aprovado com ressalva. Consulte [índice das evidências](evidencias/README.md).

## Resultados hidrológicos observados
| Indicador | VM-04 | VM-05 | VM-06 |
|---|---:|---:|---:|
| Intensidade (mm/h) | 5 | 20 | 35 |
| Vazão (L/s) | 12,396 | 52,5 | 96,979 |
| Volume (L) | 44625 | 189000 | 349125 |
| WD (mm) | 0 | 0,7927 | 2,0341 |
| Pontuação | 10 | 55 | 100 |
| Drenagem usada (L/s) | 600 | 400 | 180 |
| Drenagem cenário (L/s) | 720 | 320 | 100 |
| Classificação confiável | false | false | false |

VM-08: trecho atual BR116-264; próximos trechos BR116-265 (500 m, moderado), BR116-266 (1500 m, alto), BR116-267 (2500 m, sem análises), BR116-268 (3500 m, sem análises). Antecedência 5000 m. Distâncias são simuladas e usam comprimentos cadastrados.

## Ressalvas e próximos passos
| ID | Achado | Ação recomendada |
|---|---|---|
| OBS-001 | Simulação prioriza drenagem cadastrada do trecho, confirmado em main.py; cenário conserva seus próprios metadados | Esclarecer precedência na API e confirmar requisito com a equipe |
| OBS-002 | Renovação de alerta mantém análise original; código sincronizar_alerta atualiza apenas validade para mesmo nível | Documentar vínculo original ou definir requisito de vínculo à análise mais recente |
| OBS-003 | 404 funciona mas aparece Undocumented no Swagger | Declarar resposta 404 no OpenAPI |
| OBS-004 | Geometrias aproximadas e não validadas | Levantamento geográfico em campo |
| OBS-005 | Modelo experimental e sem calibração | Validar com dados independentes, métricas e especialistas |
| OBS-006 | Inclinação geral usada como substituta da declividade do caminho; valor não positivo pode causar ValueError; datas futuras podem ser tratadas como atuais | Criar testes específicos, confirmar entradas e tratar limites |
| OBS-007 | Frontend inicial, integrações externas não implementadas, PostgreSQL real não testado | Validar em ambiente separado; não declarar essas etapas concluídas |

## Conclusão
Os resultados históricos sustentam aprovação funcional do backend em modo mock dentro do plano executado, com ressalvas. A versão consolidada exige reteste após ajuste de indentação. Não autoriza uso operacional para navegação ou previsão de aquaplanagem.
