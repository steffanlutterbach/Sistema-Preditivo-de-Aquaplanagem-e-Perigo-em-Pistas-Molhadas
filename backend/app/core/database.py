"""Conexões PostgreSQL curtas por operação."""

from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from .config import DATABASE_URL

DATABASE_URL_CONFIGURED = DATABASE_URL


@contextmanager
def conectar():
    """Abre e fecha uma conexão; erros de rede ficam disponíveis ao chamador."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as connection:
        yield connection


def verificar_conexao() -> bool:
    with conectar() as connection:
        connection.execute("SELECT 1")
    return True
