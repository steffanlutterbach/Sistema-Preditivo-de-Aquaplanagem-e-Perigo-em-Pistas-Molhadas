# Frontend AquaSafe (React + Vite + Leaflet)

Telas que consomem a API do backend:

- **Dashboard:** simula chuva nos trechos, mostra os indicadores e a análise de cada trecho.
- **Mapa:** trechos pintados pelo nível de risco; clicar no mapa simula a posição de um motorista (`POST /monitoramento/localizacao`).
- **Alertas:** alertas ativos e histórico.

## Como rodar

1. Suba o backend (pasta `backend/`), no modo mock: `uvicorn app.main:app --reload`
2. Nesta pasta:

```bash
npm install
cp .env.example .env      # Windows: copy .env.example .env
npm run dev
```

3. Abra http://localhost:5173. No modo mock, o backend começa sem análises: no Dashboard, escolha um cenário em "Simular chuva" e clique em aplicar. Cada análise vale por 60 minutos.

Se o backend estiver com `AQUASAFE_API_KEY`, coloque a mesma chave em `VITE_API_KEY` (só para uso local).

## Organização

| Pasta | Conteúdo |
|---|---|
| `src/pages/` | Dashboard, Mapa e Alertas |
| `src/components/` | Header, Map (Leaflet), Sidebar, RiskCard, Motorista e ErroApi |
| `src/services/api.js` | Chamadas à API |
| `src/services/formatacao.js` | Números, horários e rótulos de risco |
| `src/hooks/useApi.js` | Carregamento dos dados com estado de erro |
