# Manual de instalação, operação e testes

## Pré-requisitos
Windows/PowerShell, Python 3.12 (3.12.3 observado), Node.js/npm compatíveis com Vite, VS Code opcional, navegador. Git para publicação. PostgreSQL/PostGIS apenas para modo real. Instalar Node via https://nodejs.org/pt-br/download e Python via https://www.python.org/downloads/; reabrir VS Code após instalação.

## Backend
Na raiz, execute:
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install python-dotenv
$env:DATA_MODE = "mock"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
Se ambiente já existe, não recriar. A dependência python-dotenv é importada mas não explicitada no requirements da cópia V2. Mantenha terminal aberto. Abra http://127.0.0.1:8000/docs e execute GET /health; deve retornar ok, mock, banco não utilizado.

## Frontend
Em outro terminal na raiz:
```powershell
cd frontend
node --version
npm.cmd --version
npm.cmd ci
```
Criar/editar `frontend/.env` (não o .env da raiz):
```dotenv
VITE_API_URL=http://127.0.0.1:8000
VITE_API_KEY=
```
Não usar segredo real em variáveis VITE. Salvar. Executar:
```powershell
npm.cmd run build
npm.cmd run dev
```
Acessar http://localhost:5173 (ou porta informada). Se mudar porta, verificar CORS. Não encerrar backend enquanto usa a interface.

## Utilização
Dashboard: escolher 5, 20 ou 35 mm/h e aplicar nos dez trechos; selecionar segmento para detalhes. Mapa: verificar linhas, selecionar segmento, simular motorista clicando em posição e escolhendo sentido. Alertas: consultar ativos e histórico. Estado sem análise é normal antes de simular. Reiniciar backend perde estado mock; não representa ausência de risco real.

## Testes e evidências
Com terminal na pasta backend (parar servidor se necessário):
```powershell
$env:DATA_MODE = "mock"
New-Item -ItemType Directory -Force ..\docs\validacao_v2
.\.venv\Scripts\python.exe -m pytest -v --tb=long 2>&1 | Tee-Object -FilePath ..\docs\validacao_v2\resultado_reteste_publicacao.txt
```
Na pasta frontend:
```powershell
npm.cmd run build 2>&1 | Tee-Object -FilePath ..\docs\validacao_v2\resultado_build_frontend.txt
```
Preservar logs anteriores. Conferir saída e código de retorno; 54 passed foi resultado histórico após ajustes locais, não garantia em cópia limpa.

## Diagnóstico
| Sintoma | Ação |
|---|---|
| python não reconhecido | Usar py ou executável .venv/Scripts/python.exe |
| node não reconhecido | Instalar Node/PATH e reabrir VS Code |
| npm.ps1 bloqueado | Usar npm.cmd, sem mudar política global |
| .env já existe | Editar existente, não sobrescrever credenciais |
| Erro de rede | Confirmar backend, endereço VITE_API_URL e CORS |
| 422 em testes HTTP | Conferir Content-Type e corpo; ler traceback antes de alterar testes |
| Sem análise/alerta | Executar cenário; conferir expiração e estado mock |
| Porta em uso | Verificar processo existente; não iniciar duplicado |

Encerrar servidores com Ctrl+C em cada terminal. Para banco real consultar [banco de dados](banco_de_dados.md), não utilizar simulação como operação real.
