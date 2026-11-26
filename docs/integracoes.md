# Integrações de dados

A meteorologia do AquaSafe recebe medições de precipitação e intensidade de chuva pelo endpoint `/meteorologia`. O modo `mock` usa dados locais; o modo `real` persiste no PostgreSQL os dados recebidos pelo backend.

INMET, Cemaden e DNIT permanecem fontes candidatas. Consultas externas e leitura de CSV foram removidas desta etapa. As medições devem ser enviadas manualmente pelo endpoint até retomarmos as integrações.

Estações associadas aos segmentos começam como candidatas e pendentes de validação. A API rejeita medições que indiquem uma estação sem associação validada ao segmento.

Os horários meteorológicos são normalizados em UTC. Medições vencidas ficam sinalizadas e não são usadas para classificação de risco.
