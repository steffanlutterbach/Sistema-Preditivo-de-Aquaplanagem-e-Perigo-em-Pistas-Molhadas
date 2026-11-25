"""Configurações da aplicação."""

import os

DATA_MODE = os.getenv("DATA_MODE", "mock")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aquasafe:aquasafe@localhost:5432/aquasafe",
)
