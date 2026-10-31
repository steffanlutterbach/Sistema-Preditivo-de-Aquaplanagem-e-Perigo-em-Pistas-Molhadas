# 🌧️ AquaSafe — Sistema Preditivo de Aquaplanagem

**Plataforma inteligente de monitoramento e prevenção de acidentes em rodovias durante chuvas intensas.**
---
## 📌 1. Sobre o Projeto

O **AquaSafe** é uma proposta de plataforma de monitoramento de rodovias que busca identificar trechos com maior risco de aquaplanagem durante períodos de chuva intensa.

O sistema pretende combinar informações meteorológicas, condições das rodovias e localização geográfica para calcular níveis de risco e emitir alertas preventivos aos motoristas.

O objetivo é utilizar tecnologia e dados públicos para contribuir com a segurança no trânsito e reduzir acidentes relacionados à perda de aderência dos pneus em pistas molhadas.

## ⚠️ 2. Problema Identificado

A aquaplanagem ocorre quando uma camada de água entre os pneus e o asfalto provoca perda de contato e aderência, dificultando o controle do veículo.

Esse fenômeno pode ser agravado por diferentes fatores:

- Chuvas intensas e acúmulo de água nas pistas.
- Pavimentação irregular ou desgastada.
- Deficiência nos sistemas de drenagem.
- Velocidade incompatível com as condições da rodovia.
- Falta de informações antecipadas sobre trechos perigosos.

Atualmente, motoristas podem encontrar condições perigosas sem receber alertas específicos sobre o risco de aquaplanagem na região.

**Problema central:** Como utilizar dados meteorológicos e geográficos para identificar antecipadamente trechos rodoviários com maior risco de aquaplanagem e alertar os motoristas?

## 💡 3. Proposta de Solução

O AquaSafe propõe uma plataforma capaz de analisar dados de chuva e características das rodovias para identificar possíveis situações de risco.

Inicialmente, o sistema utilizará regras predefinidas para classificar trechos monitorados em três níveis:

- 🟢 **Risco Baixo:** Condições de chuva abaixo dos limites de alerta estabelecidos.
- 🟡 **Risco Moderado:** Precipitação elevada ou presença de condições que exigem atenção.
- 🔴 **Risco Alto:** Combinação de chuva intensa com características conhecidas de maior vulnerabilidade da pista.

Quando um trecho atingir o nível de risco alto, o sistema deverá gerar um alerta geolocalizado para motoristas próximos.

### Funcionamento Proposto

1. A rodovia monitorada será dividida em segmentos de aproximadamente 1 km.
2. Cada segmento possuirá informações geográficas e características da pista.
3. O sistema consultará dados meteorológicos disponíveis para a região.
4. Um algoritmo analisará a precipitação e os fatores de risco cadastrados.
5. O trecho receberá uma classificação de risco.
6. Caso o risco seja elevado, o sistema acionará o serviço responsável pelos alertas.
7. O motorista poderá visualizar uma notificação indicando a localização do perigo.

**Observação:** A classificação inicial será baseada em regras e limites experimentais. Ela representa uma estimativa preventiva, não uma previsão física precisa da ocorrência de aquaplanagem.

## 🛠️ 4. Tecnologias Propostas

| Tecnologia | Aplicação |
|---|---|
| Python | Processamento de dados e cálculo dos níveis de risco |
| FastAPI | Desenvolvimento da API e dos microsserviços |
| PostgreSQL | Armazenamento das informações dos trechos |
| PostGIS | Gerenciamento de coordenadas e consultas geográficas |
| React | Desenvolvimento da interface web |
| JavaScript | Interatividade e integração com a API |
| Leaflet | Visualização dos trechos em um mapa interativo |
| HTML e CSS | Estrutura e estilização da plataforma |
| Git e GitHub | Versionamento, documentação e colaboração |

Essas tecnologias representam a proposta inicial e poderão ser ajustadas conforme o desenvolvimento do projeto.

## 🌐 5. Fontes de Dados

O projeto pretende utilizar bases públicas e serviços de informação relacionados às condições meteorológicas e rodoviárias.

| Fonte | Dados pretendidos |
|---|---|
| DNIT | Informações e localização de rodovias federais |
| INMET | Dados de precipitação de estações meteorológicas |
| Cemaden | Dados de monitoramento pluviométrico |
| Waze | Possíveis relatos complementares de condições perigosas, mediante disponibilidade e autorização de acesso |

A integração dependerá da disponibilidade, cobertura geográfica, frequência de atualização e condições de acesso de cada fonte.

Durante o MVP, poderão ser utilizados dados históricos ou simulados para validar a lógica de funcionamento.

## 🧩 6. MVP — Produto Mínimo Viável

A primeira versão funcional terá como objetivo demonstrar a identificação de trechos perigosos e a geração de alertas simulados.

### Funcionalidades Principais

**1. Cadastro e segmentação de rodovias**

- Armazenar informações de uma rodovia selecionada.
- Dividir a rodovia em trechos de aproximadamente 1 km.
- Registrar coordenadas e fatores conhecidos de vulnerabilidade.

**2. Monitoramento da precipitação**

- Consultar dados de chuva de uma fonte disponível.
- Associar as medições aos trechos monitorados.
- Permitir a utilização de dados simulados para testes.

**3. Classificação automática de risco**

- Analisar a intensidade da chuva.
- Considerar informações cadastradas sobre as condições da pista.
- Classificar os trechos nos níveis baixo, moderado e alto.

**4. Simulação de notificações**

- Identificar quando um trecho atingir risco alto.
- Acionar um microsserviço de alertas.
- Simular o envio de uma notificação para motoristas localizados na região.

**5. Visualização em mapa**

- Exibir os trechos monitorados.
- Utilizar cores para representar o nível de risco.
- Permitir a consulta das condições de cada segmento.

### Exemplo de Funcionamento

**Cenário hipotético:**

- Rodovia: BR-116.
- Trecho monitorado: km 120 ao km 121.
- Intensidade da chuva: 35 mm/h.
- Condição cadastrada: Pavimentação irregular.
- Limite experimental de alerta: 30 mm/h.

**Resultado esperado:**

🔴 **RISCO ALTO — POSSÍVEL AQUAPLANAGEM**

O sistema identifica a combinação de precipitação acima do limite experimental e condições desfavoráveis da pista.

Uma notificação simulada é gerada:

> ⚠️ Atenção! Risco elevado de aquaplanagem no próximo trecho da rodovia. Reduza a velocidade com segurança e aumente a distância do veículo à frente.

Os valores utilizados neste exemplo são ilustrativos e não representam limites técnicos validados de segurança viária.

## 🏗️ 7. Arquitetura Inicial do Sistema

O AquaSafe será organizado em componentes independentes para facilitar manutenção e expansão.

         FONTES DE DADOS
       INMET / Cemaden / DNIT
                 |
                 v
        COLETA DE INFORMAÇÕES
                 |
                 v
        BACKEND — PYTHON
             FastAPI
                 |
        +--------+--------+
        |                 |
        v                 v
   PostgreSQL       Motor de Risco
    + PostGIS        por Trecho
        |                 |
        +--------+--------+
                 |
                 v
           API DE RISCO
                 |
        +--------+--------+
        |                 |
        v                 v
   Interface Web     Microsserviço
   React + Leaflet    de Alertas
        |                 |
        v                 v
   Mapa de Riscos    Notificação
                      Simulada

## 🎨 8. Identidade Visual

A identidade visual do AquaSafe será inspirada em segurança viária, tecnologia e monitoramento meteorológico.

### Nome

**AquaSafe**

O nome combina *Aqua* (água) com *Safe* (segurança), representando o propósito de prevenir situações perigosas provocadas pela presença de água nas rodovias.

### Paleta de Cores

| Cor | Código | Significado |
|---|---|---|
| Azul-escuro | `#102A43` | Tecnologia, confiança e segurança |
| Azul-claro | `#38BDF8` | Água e monitoramento meteorológico |
| Verde | `#22C55E` | Risco baixo |
| Amarelo | `#FACC15` | Risco moderado |
| Vermelho | `#EF4444` | Risco alto |
| Branco | `#FFFFFF` | Clareza e legibilidade |

### Conceito de Logotipo

O logotipo proposto combinará uma **rodovia estilizada com uma gota de água e um símbolo de alerta**, representando a relação entre chuva, trânsito e prevenção.

### Interface

A interface será desenvolvida com foco em:

- Visual moderno e responsivo.
- Mapa interativo como elemento principal.
- Identificação rápida dos níveis de risco.
- Alertas visíveis e de fácil compreensão.
- Navegação simples para usuários e administradores.

## 🎯 9. Objetivos

### Objetivo Geral

Desenvolver um protótipo de plataforma capaz de identificar e sinalizar trechos rodoviários com potencial risco de aquaplanagem utilizando dados meteorológicos e informações geográficas.

### Objetivos Específicos

- Integrar dados meteorológicos e rodoviários.
- Organizar trechos de rodovias em um banco de dados geográfico.
- Implementar um algoritmo inicial de classificação de risco.
- Desenvolver uma API para disponibilizar os resultados.
- Criar um mapa interativo dos trechos monitorados.
- Implementar um serviço de simulação de alertas geolocalizados.
- Realizar testes com diferentes cenários de precipitação.

## 🚀 10. Evoluções Futuras

Após o desenvolvimento e validação do MVP, poderão ser estudadas novas funcionalidades:

- Modelos de aprendizado de máquina para análise de padrões.
- Integração com aplicativos de navegação.
- Notificações push reais em dispositivos móveis.
- Utilização de sensores de umidade e condições do pavimento.
- Análise de históricos de acidentes.
- Ampliação do monitoramento para diferentes rodovias.
- Painel administrativo para concessionárias e órgãos públicos.

Essas funcionalidades não fazem parte do escopo obrigatório da primeira versão.

## 📅 11. Etapas do Projeto

| Etapa | Entrega | Foco |
|---|---|---|
| Checkpoint 1 | Ideação | Problema, proposta de solução, tecnologias, identidade visual e pitch |
| Checkpoint 2 | Desenvolvimento inicial | Estrutura do banco de dados, API e primeiras funcionalidades |
| Checkpoint 3 | MVP funcional | Integração dos componentes, testes e apresentação do protótipo |

As etapas posteriores representam um planejamento inicial, sujeito ao cronograma oficial da disciplina.

## 🎤 12. Pitch Inicial

**E se fosse possível identificar uma pista perigosa antes que o motorista perdesse o controle do veículo?**

Durante chuvas intensas, rodovias podem apresentar condições que favorecem a aquaplanagem, aumentando o risco de acidentes graves.

O **AquaSafe** surge como uma proposta tecnológica para ajudar a enfrentar esse problema.

A plataforma combinará dados meteorológicos e informações geográficas para identificar trechos com maior risco e gerar alertas preventivos.

Por meio de uma interface simples e de um mapa interativo, o sistema permitirá visualizar as condições das rodovias e receber informações sobre possíveis perigos.

**AquaSafe — Antecipando riscos, protegendo caminhos.**

---

## 📚 13. Referências e Fontes Oficiais

- [DNIT — Departamento Nacional de Infraestrutura de Transportes](https://www.gov.br/dnit/pt-br)
- [INMET — Instituto Nacional de Meteorologia](https://portal.inmet.gov.br/)
- [Cemaden — Centro Nacional de Monitoramento e Alertas de Desastres Naturais](https://www.gov.br/cemaden/pt-br)
- [Documentação do Python](https://docs.python.org/3/)
- [Documentação do FastAPI](https://fastapi.tiangolo.com/)
- [Documentação do PostgreSQL](https://www.postgresql.org/docs/)
- [Documentação do PostGIS](https://postgis.net/documentation/)
- [Documentação do React](https://react.dev/)
- [Documentação do Leaflet](https://leafletjs.com/)

---

## 📄 14. Status do Projeto

**Checkpoint 1 — Ideação concluída em nível de proposta.**

O projeto encontra-se em fase de planejamento. As tecnologias, funcionalidades e integrações descritas representam o escopo pretendido, não funcionalidades já implementadas.

Este repositório será utilizado para centralizar o código-fonte, a documentação e a evolução do AquaSafe ao longo do semestre.

---

**AquaSafe © 2026 — Tecnologia para um trânsito mais seguro.**
