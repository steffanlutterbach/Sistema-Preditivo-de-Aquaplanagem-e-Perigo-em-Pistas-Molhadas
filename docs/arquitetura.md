# Arquitetura

O AquaSafe separa dados, integração, backend, banco geográfico e interface.

Fontes → camada de integração → FastAPI → PostgreSQL/PostGIS e serviços de negócio → API REST → React/Leaflet.
