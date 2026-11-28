# Relatório de validação funcional V2 — 28/11/2026

## Escopo e ambiente
Windows, VS Code, Python 3.12.3, pytest, FastAPI/Uvicorn, Swagger, Node/npm, React/Vite/Leaflet, navegador. Backend em DATA_MODE=mock. Revisão de código da cópia V2 enviada, evidências locais e confirmação final do responsável. Não reexecutamos os testes nesta consolidação. A aprovação é funcional e não certifica a precisão preditiva.

## Testes automatizados
| Rodada | Aprovados | Falhas | Duração |
|---|---:|---:|---:|
| 1 | 30 | 24 | 2,48 s |
| 2 | 52 | 2 | 1,63 s |
| 3 | 54 | 0 | 1,70 s |

NC-V2-001: auxiliar HTTP sem Content-Type JSON; inclusão do cabeçalho eliminou 22 falhas. NC-V2-002: teste Via Dutra exigia WD apesar de declividade ausente; passou a verificar indisponibilidade e cálculo condicional após PATCH com valor artificial. NC-V2-003: expectativa de origem antiga `simulado_fornecido_pelo_usuario` substituída por `mock`, conforme cadastro. As últimas duas ações adequaram testes, não o motor. Evidências: log inicial e screenshots dos retestes. Os logs TXT da segunda/terceira rodada e do build estão no computador do responsável e devem ser preservados; não foram recebidos como arquivos completos nesta consolidação.

## Testes manuais API
| ID | Entrada | HTTP | Resultado observado |
|---|---|---:|---|
| V2-01 | GET /health | 200 | ok, mock |
| V2-02 | GET /rodovias | 200 | duas regiões |
| V2-03 | GET /trechos | 200 | dez trechos; ressalva de metadados |
| V2-04 | GET /trechos?rodovia_id=1 | 200 | IDs 1–5 |
| V2-05 | GET /trechos?rodovia_id=2 | 200 | IDs 6–10; ressalva de metadados |
| V2-06 | GET /mapa/riscos | 200 | dez LineString em FeatureCollection |
| V2-07 | POST /simulacoes, cenário 1 trecho 1 | 200 | baixo, 10, sem alerta |
| V2-08 | cenário 2 trecho 2 | 200 | moderado, 55, alerta |
| V2-09 | cenário 3 trecho 3 | 200 | alto, 100, alerta |
| V2-10 | cenário 2 trecho 8 | 200 | alto, 70, alerta |
| V2-11 | GET /alertas?historico=false | 200 | três ativos, chaves distintas |
| V2-12 | POST /monitoramento/localizacao, região 1 | 200 | trecho 1, alertas 2/3; ressalva distância |
| V2-13 | região 2 | 200 | trecho 6, alerta 8; ressalva distância |
| V2-14 | latitude 100 longitude 200 | 422 | ambas rejeitadas |
| V2-15 | GET /meteorologia/estacoes | 200 | cinco estações |
| V2-16 | INMET 12,5 mm, trecho 1 sem estação | 200 | ID 6, intensidade nula; tentativa inicial com estação pendente rejeitada 422 |
| V2-17 | CEMADEN 8,5 mm trecho 1 | 200 | ID 7, intensidade nula |
| V2-18 | INMET 15 mm repetido | 200/409 | ID 8 aceito, duplicado rejeitado |
| V2-19 | FONTE_TESTE | 422 | fonte rejeitada |
| V2-20 | GET /trechos/9999 | 404 | trecho não encontrado |

Os 20 casos atenderam aos critérios principais; não implica aprovação de todos os atributos. V2-07–10 apresentam lacuna de rastreabilidade, WD nula por ausência de declividade. Drenagem vem do cadastro do trecho. V2-12/13 isolam regiões, mas a distância longitudinal permanece questionável.

| Cenário/trecho | Q L/s | V L | Pontuação | Risco |
|---|---:|---:|---:|---|
| 1/1 | 12,396 | 44.625 | 10 | baixo |
| 2/2 | 52,5 | 189.000 | 55 | moderado |
| 3/3 | 96,979 | 349.125 | 100 | alto |
| 2/8 | 76,667 | 276.000 | 70 | alto |

## Frontend e integração
| ID | Teste | Resultado / evidência |
|---|---|---|
| VF-01 | Build | Aprovado; 84 módulos, 2,03 s, print |
| VF-02 | Inicialização | Aprovado; Vite 6.4.6, interface aberta |
| VF-03 | Dashboard | Aprovado; dez trechos em print |
| VF-04 | Chuva fraca | Vídeo: 8 baixos, 2 moderados, máximo 40; detalhes finais confirmados pelo responsável |
| VF-05 | Chuva moderada | Vídeo: 8 moderados, 2 altos, máximo 70; detalhes finais confirmados pelo responsável |
| VF-06 | Chuva intensa | Vídeo: 10 altos, máximo 100 |
| VF-07 | Renderização mapa | Observado no vídeo |
| VF-08 | Duas regiões | Observado no escopo visual; sem validação cartográfica oficial |
| VF-09 | Seleção e detalhes | Observado no vídeo |
| VF-10 | Cores de risco | Parcial no vídeo; conclusão confirmada pelo responsável, sem captura final |
| VF-11 | Motorista | Observado no vídeo; ressalva distância |
| VF-12 | Sentido | Conclusão confirmada pelo responsável, sem captura final |
| VF-13 | Alertas ativos | Observado no vídeo |
| VF-14 | Histórico | Observado no vídeo |
| VF-15 | Backend indisponível | Confirmado pelo responsável, sem captura final |
| VF-16 | Responsividade | Confirmado pelo responsável, sem captura final |

O responsável informou que os últimos testes estavam corretos. Registra-se confirmação declarada, não evidência independente nem verificação de todos os dispositivos. 12 casos com critérios principais observados anteriormente (alguns com ressalvas) e quatro concluídos por declaração; detalhes complementares de VF-04/05 também declarados.

## Ressalvas e critérios de encerramento
| ID | Observação | Prioridade |
|---|---|---|
| OBS-V2-001 | origem_geometria Via Dutra contém referência km 264–269 incorreta | Média |
| OBS-V2-002 | POST /simulacoes não passa todos os campos de proveniência para analisar_trecho | Média |
| OBS-V2-003 | Distância zero até próximo segmento em duas posições; fração local de uma aresta usada como fração do trecho inteiro | Alta |
| OBS-V2-004 | 404 e 409 aparecem Undocumented no Swagger | Baixa |

A análise estática indica causa provável de OBS-V2-003, ainda não confirmada por reteste corretivo. Não houve alteração de código nesta entrega. Validar distância acumulada por todas as arestas, sentido e limites antes de uso real. Resultado consolidado: validação funcional mock concluída no escopo planejado, com ressalvas e confirmação declarada dos testes finais. PostgreSQL real, integrações ao vivo, calibração física e segurança operacional não validados.
