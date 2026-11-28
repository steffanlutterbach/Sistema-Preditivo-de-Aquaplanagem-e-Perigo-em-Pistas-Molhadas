
import os

import psycopg
from dotenv import load_dotenv

# Carrega as configurações do arquivo .env
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "aquasafe"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


def conectar_banco():
    """Cria uma conexão com o banco de dados AquaSafe."""
    if not DB_CONFIG["password"]:
        raise ValueError("DB_PASSWORD não foi configurada no arquivo .env")

    return psycopg.connect(**DB_CONFIG)


def testar_conexao():
    """Verifica se a conexão com PostgreSQL está funcionando."""
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            resultado = cursor.fetchone()
            return resultado[0]
