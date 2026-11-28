# Arquitetura do sistema

Aplicação web cliente-servidor, com backend modular FastAPI (não um conjunto de microsserviços implantados), interface React/Vite e dois modos de persistência.

```mermaid
flowchart LR
 U[Usuário] --> F[React / Vite]
 F -->|HTTP JSON| A[FastAPI / Uvicorn]
 F --> L[Leaflet / mapa OSM]
 A --> S[Serviços de cálculo, risco e monitoramento]
 A --> N[Normalização INMET / Cemaden]
 S --> R[Repositórios]
 N --> R
 A --> R
 R -->|mock| M[JSON + memória]
 R -->|real| P[(PostgreSQL / PostGIS)]
```

| Caminho | Responsabilidade |
|---|---|
| backend/app/main.py | Composição da API, CORS, chave, health, mapa e simulações |
| backend/app/api/routes/ | Rodovias, trechos, análises, meteorologia, alertas e localização |
| backend/app/schemas/ | Contratos Pydantic e validação de entrada |
| backend/app/core/ | Configuração e conexão ao banco |
| backend/app/services/ | Hidrologia, classificação, alertas, correspondência geográfica |
| backend/app/repositories/ | Abstração mock/real, consultas e persistência |
| backend/app/integrations/ | Normalização e módulos candidatos de integração |
| backend/tests/ | Testes automatizados |
| frontend/src/ | Páginas, componentes, hooks, serviços HTTP e estilos |
| database/migrations/ | Evolução SQL manual |
| mock_data/ | Cadastros e cenários demonstrativos |
| docs/ | Documentação e evidências |

## Fluxo de simulação
```mermaid
sequenceDiagram
 participant U as Usuário
 participant F as Frontend
 participant A as API
 participant R as Repositório
 U->>F: Escolher chuva e aplicar
 loop Cada trecho cadastrado
 F->>A: POST /simulacoes
 A->>R: Consultar cenário e trecho
 A->>A: Calcular vazão, volume, risco e WD se disponível
 A->>R: Registrar em mock e sincronizar alerta
 A-->>F: Resultado JSON
 end
 F->>A: Consultar resultados e alertas
 F-->>U: Atualizar indicadores
```

O mapa consome `/mapa/riscos` em GeoJSON; a posição é enviada a `/monitoramento/localizacao`. O modo real usa PostgreSQL/PostGIS e exige chave de API; o banco não foi exercitado na campanha. Não há coleta externa automática nem serviço de notificações push operacional.
