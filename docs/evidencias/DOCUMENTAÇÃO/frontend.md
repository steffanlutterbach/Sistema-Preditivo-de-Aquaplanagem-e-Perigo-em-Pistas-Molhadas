# Frontend — React, Vite e Leaflet

Interface SPA com React 18, Vite 6 e Leaflet 1.9 (React-Leaflet 4). Dependências registradas em package.json e lockfile. Scripts: `npm.cmd ci`, `npm.cmd run build`, `npm.cmd run dev`, `npm.cmd run preview` (preview do build).

| Componente | Responsabilidade |
|---|---|
| App.jsx / main.jsx | Inicialização e composição das páginas |
| pages/Dashboard.jsx | Indicadores, seleção de chuva, simulação em dez trechos, detalhes |
| pages/Mapa.jsx | Mapa e monitoramento de motorista |
| pages/Alertas.jsx | Alertas ativos e histórico |
| components/Map/MapaRiscos.jsx | GeoJSON e interação cartográfica |
| components/Motorista/PainelMotorista.jsx | Posição simulada e sentido |
| components/RiskCard/ | Detalhes de risco |
| components/ErroApi/ | Apresentação de falhas de comunicação |
| services/api.js | fetch, JSON, cabeçalhos e tratamento de erro HTTP |
| services/formatacao.js | Formatação dos resultados |
| hooks/useApi.js | Estado de consulta |
| styles/global.css | Estilos e layout |

## Configuração
`frontend/.env`: `VITE_API_URL=http://127.0.0.1:8000` e `VITE_API_KEY=` no mock sem chave. O código usa localhost:8000 como fallback. Variáveis VITE são públicas no bundle; nunca colocar segredo de produção nelas. O backend permite por padrão localhost:5173 e 127.0.0.1:5173 via CORS.

## Operação
Dashboard começa sem análises válidas após reiniciar o mock. Escolher chuva e clicar em Aplicar nos 10 trechos; selecionar segmento para detalhes. Mapa apresenta linhas e classificação; verde/ amarelo/ vermelho representam baixo/ moderado/ alto, e estado sem análise deve permanecer distinguível. Painel motorista permite simular ponto e sentido, sem usar a interface como navegação real. Alertas mostra ativos e histórico. Erros de rede devem ser apresentados sem indicar falsamente dados atuais.

## Verificação
Build observado: Vite 6.4.6 em execução, 84 módulos, compilação em 2,03 s, HTML 0,46 kB, CSS 20,90 kB, JS 312,88 kB (tamanhos do build local). Vídeo e imagens em [evidências](validacao_v2/evidencias_frontend/). Ver [relatório](validacao_v2/RELATORIO_VALIDACAO_V2.md) para distinção entre observação e confirmação do responsável.
