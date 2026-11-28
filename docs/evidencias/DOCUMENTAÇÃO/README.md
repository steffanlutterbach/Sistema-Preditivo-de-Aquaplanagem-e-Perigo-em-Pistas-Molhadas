# AquaSafe — Sistema Preditivo de Aquaplanagem e Perigo em Pistas Molhadas

Protótipo acadêmico funcional de monitoramento experimental de risco em rodovias. Combina dados de precipitação, condições de pista, drenagem e geometria para classificar segmentos e apresentar alertas em uma interface web.

**Estado em 28/11/2026:** backend e frontend executados localmente em modo mock; 54 testes automatizados aprovados após ajustes nos testes, 20 casos manuais da API com critérios principais atendidos e 16 casos de frontend executados/confirmados pelo responsável (parte sem evidência independente). Não é um sistema operacional de segurança viária nem uma previsão cientificamente validada.

## Funcionalidades
- Dez segmentos demonstrativos da BR-116, cinco na Régis Bittencourt (km 264–269) e cinco na Via Dutra (km 225–230).
- Simulação de chuva de 5, 20 e 35 mm/h, classificação experimental baixo/moderado/alto e alertas.
- Dashboard React, mapa Leaflet/GeoJSON, histórico de alertas e simulação de motorista.
- Cadastro e atualização de trechos, medições e estações; normalização de entradas INMET/Cemaden fornecidas manualmente.
- Modo mock em memória e estrutura de persistência PostgreSQL/PostGIS em modo real (não validado nesta campanha).

## Execução rápida — Windows / PowerShell
Na raiz do projeto, terminal 1:
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install python-dotenv
$env:DATA_MODE = "mock"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
No terminal 2, a partir da raiz:
```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```
Configure `frontend/.env` antes de iniciar: `VITE_API_URL=http://127.0.0.1:8000` e `VITE_API_KEY=` (mock sem chave configurada). Não publique credenciais. API: http://127.0.0.1:8000/docs ; interface: http://localhost:5173 .

## Documentação
| Documento | Conteúdo |
|---|---|
| [Documentação técnica](docs/DOCUMENTACAO.md) | Escopo, dados, regras e algoritmos |
| [Requisitos](docs/REQUISITOS.md) | Requisitos e rastreabilidade |
| [Arquitetura](docs/arquitetura.md) | Componentes e fluxos |
| [API](docs/endpoints.md) | Rotas e contratos |
| [Frontend](docs/frontend.md) | Componentes, interface e integração |
| [Banco](docs/banco_de_dados.md) | Modelo e migrations |
| [Integrações](docs/integracoes.md) | Fontes, proveniência e limitações |
| [Manual](docs/MANUAL.md) | Instalação, uso e diagnóstico |
| [Validação](docs/VALIDACAO.md) | Resultados V1 e V2, evidências e ressalvas |
| [Manutenção](docs/MANUTENCAO.md) | Pendências, segurança e publicação |
| [Proposta original](docs/PROPOSTA_INICIAL.md) | Histórico de concepção |

## Limites de utilização
Geometrias e parâmetros são demonstrativos; não usar para navegação ou decisões de condução. Não há coleta automática de estações, confirmação de quilometragem oficial ou calibração científica. A pontuação não é probabilidade de acidente. Dados cartográficos derivados do OpenStreetMap: © colaboradores do OpenStreetMap, ODbL. Consulte [atribuição](https://www.openstreetmap.org/copyright).
