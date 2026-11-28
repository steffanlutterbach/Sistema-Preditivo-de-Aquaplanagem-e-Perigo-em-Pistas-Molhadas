# Requisitos e matriz de rastreabilidade

Os requisitos abaixo descrevem o MVP atual e seus critérios verificáveis. Identificadores são atribuídos nesta consolidação para rastreabilidade; não representam uma especificação formal aprovada anteriormente.

| ID | Requisito funcional | Critério de aceitação | Evidência V2 |
|---|---|---|---|
| RF01 | Consultar disponibilidade | Health retorna 200 e modo correto | V2-01 |
| RF02 | Consultar rodovias e trechos | Duas rodovias, dez trechos, filtro exclusivo | V2-02–05, VF-03 |
| RF03 | Cadastrar/alterar trecho | Validar parâmetros, retornar registro | Suíte automatizada; sem teste manual dedicado |
| RF04 | Expor geometria | FeatureCollection com dez LineString | V2-06, VF-07–09 |
| RF05 | Executar cenários | Resposta com risco, vazão, volume e estado | V2-07–10, VF-04–06 |
| RF06 | Gerar e consultar alertas | Moderado/alto geram alerta válido; baixo não | V2-07–11, VF-13–14 |
| RF07 | Processar posição | Identificar segmento, mesma rodovia e sentido | V2-12–13, VF-11–12; ressalva distância |
| RF08 | Rejeitar coordenadas inválidas | HTTP 422 | V2-14 |
| RF09 | Consultar estações e associações | Lista e status identificáveis | V2-15 |
| RF10 | Normalizar dados externos | Preservar fonte, precipitação e timestamp | V2-16–17 |
| RF11 | Rejeitar duplicidade/fonte inválida | 409/422 | V2-18–19 |
| RF12 | Tratar recurso inexistente | 404 e mensagem | V2-20 |
| RF13 | Mostrar painel e detalhes | Dez trechos, indicadores, estados de risco | VF-02–06 |
| RF14 | Mostrar mapa e cores | Coerência com classificação | VF-07–10 |
| RF15 | Consultar histórico e atualizar alerta | Histórico, validade e deduplicação | V2-11, VF-13–14, suíte |
| RF16 | Calcular WD condicionalmente | Não substituir declividade ausente; calcular com dados válidos | Suíte e V2-07–10 |
| RF17 | Registrar rastreabilidade | Origem dos insumos e geometria | Suíte; lacuna em simulações OBS-V2-002 |
| RF18 | Persistir no banco real | Gravação e consultas coerentes após reinício | Não validado em PostgreSQL real |
| RF19 | Isolar simulação do banco operacional | Simulação real não persiste | Suíte automatizada com isolamento simulado |

| ID | Requisito não funcional | Critério / situação |
|---|---|---|
| RNF01 | Reprodutibilidade | Comandos de instalação, lockfile e suíte; build e testes locais registrados |
| RNF02 | Validação de entradas | Pydantic e erros HTTP; V2-14,18,19,20 |
| RNF03 | Controle de acesso | Chave configurável, obrigatória em real; testes automatizados, não auditoria de segurança |
| RNF04 | Privacidade | Posição não persistida segundo resposta; sem auditoria integral de logs/rede |
| RNF05 | Resiliência | Erro de API tratado; VF-15 confirmado pelo responsável, sem captura final |
| RNF06 | Usabilidade e responsividade | Navegação e layout; VF-16 confirmado pelo responsável, sem captura final |
| RNF07 | Transparência | Dados simulados e classificação não confiável identificados; geometrias não validadas |
| RNF08 | Desempenho | Tempos locais registrados; sem SLA, benchmark concorrente ou teste de carga |
| RNF09 | Manutenibilidade | Separação de rotas, serviços, repositórios e UI; documentação e testes |
| RNF10 | Segurança viária | Não usar como orientação operacional; validação científica e espacial pendentes |

## Fora do escopo do MVP
Coleta automática e contínua, notificações push reais, previsão física calibrada, implantação em produção, auditorias de segurança e acessibilidade, testes de carga e validação oficial de campo.
