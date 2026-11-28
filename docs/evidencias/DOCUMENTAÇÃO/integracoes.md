# Integrações e origem dos dados

| Fonte | Uso implementado | Limite |
|---|---|---|
| INMET | Normalização de observação recebida por API | Sem consulta ao vivo; duas estações candidatas |
| Cemaden | Normalização de observação recebida por API | Sem feed ao vivo; duas associações mock marcadas validadas |
| DNIT | Referência pretendida de rodovia e engenharia | Sem integração operacional comprovada |
| OpenStreetMap | Traçados usados no cadastro e mapa Leaflet | Quilometragem oficial e precisão espacial não confirmadas |
| Waze | Fonte complementar considerada na proposta original | Não implementada |

Estação 1 Cemaden Butantã/Vila Sônia, 2 INMET A701 e 3 INMET A771: candidatas aos trechos 1–5. Estação 4 Cemaden Vila Maria/Parque Novo Mundo (355030885A): trechos 6–8. Estação 5 Cemaden Santana/Carandiru (355030843A): trechos 9–10. As duas últimas possuem validação apenas de teste; coordenadas e distâncias não cadastradas. A API bloqueia associação pendente quando estação é informada. Sem estação, normalização mock aceita observação manual; não prova representatividade da estação.

Timestamps normalizados em UTC; distinguir precipitação acumulada (mm) de intensidade (mm/h). A rota externa não presume intensidade sem dados temporais suficientes. Fonte, trecho e data/hora formam o critério de duplicidade observado. Não confundir cadastro de fonte com integração automática.

Atribuição cartográfica: © colaboradores do OpenStreetMap, ODbL, https://www.openstreetmap.org/copyright. Referências candidatas para hidrologia citadas no projeto: DNIT IPR-715 e Gallaway (1979); verificar edição, equação, unidades e aplicabilidade antes de validar cientificamente. Nenhuma verificação bibliográfica externa foi realizada nesta consolidação.
