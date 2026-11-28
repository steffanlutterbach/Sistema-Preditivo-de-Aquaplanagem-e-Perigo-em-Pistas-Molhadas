
"""Configurações da aplicação."""

import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg.conninfo import make_conninfo

# Carrega o .env localizado na raiz do projeto.
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

DATA_MODE = os.getenv("DATA_MODE", "mock").strip().lower()
if DATA_MODE not in {"mock", "real"}:
    raise ValueError("DATA_MODE deve ser 'mock' ou 'real'")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = make_conninfo(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "aquasafe"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )

METEOROLOGY_STALE_MINUTES = int(os.getenv("METEOROLOGY_STALE_MINUTES", "60"))
ALERT_VALIDITY_MINUTES = int(os.getenv("ALERT_VALIDITY_MINUTES", "30"))
ALERT_LEAD_DISTANCE_METERS = float(os.getenv("ALERT_LEAD_DISTANCE_METERS", "5000"))
LOCATION_MATCH_TOLERANCE_METERS = float(os.getenv("LOCATION_MATCH_TOLERANCE_METERS", "350"))

if (
    METEOROLOGY_STALE_MINUTES <= 0
    or ALERT_VALIDITY_MINUTES <= 0
    or ALERT_LEAD_DISTANCE_METERS <= 0
    or LOCATION_MATCH_TOLERANCE_METERS <= 0
):
    raise ValueError(
        "Limites de atualidade, validade e localização devem ser positivos"
    )

API_KEY = os.getenv("AQUASAFE_API_KEY", "").strip()

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

if DATA_MODE == "real" and not API_KEY:
    raise ValueError("AQUASAFE_API_KEY é obrigatório quando DATA_MODE=real")
