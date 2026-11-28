# Manutenção, segurança e publicação

## Pendências técnicas
- OBS-V2-001: revisar origem_geometria de IDs 6–10, JSON e migration correspondente; manter geometria_validada=false sem levantamento.
- OBS-V2-002: propagar fonte_meteorologia, modo_meteorologia, origem_trecho, origem_geometria, geometria_validada na rota de simulação, como em /analises; adicionar teste de regressão da rota.
- OBS-V2-003: corrigir fração longitudinal acumulando extensão das arestas antes/depois do ponto projetado; validar ambos os sentidos, vértices, limites e segmentos fora de tolerância. Não usar distância atual para navegação.
- OBS-V2-004: declarar respostas 404/409 com modelos de erro no OpenAPI e revisar demais erros.
- Declarar python-dotenv em requirements; testar ambiente limpo; considerar pinagem de versões e CI. Verificar correspondência entre fonte da medição e fonte da estação quando fornecida.
- Validar migrations em banco isolado, integridade, backup e restauração; testar autenticação e concorrência; não confundir dados mock com reais.
- Validar estações, geometria e parâmetros de drenagem em campo; calibrar modelo com dados independentes, revisar referências e métricas de erro.

## Segurança
Não commitar .env, .venv, node_modules, dist, caches e credenciais. Variáveis VITE são públicas. Chave compartilhada não equivale a controle de acesso por usuário. Para implantação futura, HTTPS, autenticação adequada, restrições CORS, gestão de segredos, logs sem coordenadas sensíveis e revisão de segurança. Não há auditoria formal realizada.

## Publicar documentação
Copiar README.md e mesclar docs/ na raiz do clone local, preservando arquivos locais e logs de V2. Não substituir backend/frontend com versões anteriores. Antes de commit, verificar `git status`, `git diff`, e se `.env` e diretórios gerados estão ignorados. Preparar README.md e docs/ e o arquivo de testes atualizado, após reteste. Inspecionar `git diff --cached --stat`; realizar commit e push. Se a pasta veio de Download ZIP e não contém .git, clonar o repositório em outra pasta primeiro, copiar documentação e somente as alterações de código realmente testadas. Não inicializar um repositório novo sobre o ZIP nem forçar push.
