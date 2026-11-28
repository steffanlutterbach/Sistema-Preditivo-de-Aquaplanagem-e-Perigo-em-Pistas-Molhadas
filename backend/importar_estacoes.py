
from pathlib import Path
import json

from database import conectar_banco

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_ESTACOES = BASE_DIR / "mock_data" / "estacoes.json"


def carregar_estacoes():
    with open(ARQUIVO_ESTACOES, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def importar_estacoes(cursor, estacoes):
    for estacao in estacoes:
        coordenadas = estacao.get("coordenadas")

        latitude = None
        longitude = None

        if coordenadas:
            latitude = coordenadas.get("latitude")
            longitude = coordenadas.get("longitude")

        cursor.execute(
            """
            INSERT INTO estacoes (
                id,
                codigo_externo,
                fonte,
                nome,
                origem_dados,
                status_associacao,
                latitude,
                longitude,
                observacao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                codigo_externo = EXCLUDED.codigo_externo,
                fonte = EXCLUDED.fonte,
                nome = EXCLUDED.nome,
                origem_dados = EXCLUDED.origem_dados,
                status_associacao = EXCLUDED.status_associacao,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                observacao = EXCLUDED.observacao
            """,
            (
                estacao["id"],
                estacao["codigo_externo"],
                estacao["fonte"],
                estacao["nome"],
                estacao.get("origem_dados"),
                estacao.get("status_associacao"),
                latitude,
                longitude,
                estacao.get("observacao"),
            ),
        )

    print(f"{len(estacoes)} estação(ões) importada(s).")


def ajustar_sequencia(cursor):
    cursor.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('public.estacoes', 'id'),
            COALESCE((SELECT MAX(id) FROM estacoes), 1),
            EXISTS (SELECT 1 FROM estacoes)
        );
        """
    )


def main():
    estacoes = carregar_estacoes()

    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            importar_estacoes(cursor, estacoes)
            ajustar_sequencia(cursor)

    print("Importação das estações concluída!")


if __name__ == "__main__":
    main()
