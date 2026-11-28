
import json
from pathlib import Path

from database import conectar_banco

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_TRECHOS = BASE_DIR / "mock_data" / "trechos.json"


def carregar_trechos():
    with open(ARQUIVO_TRECHOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)



def importar_condicoes(cursor, trechos):
    for trecho in trechos:
        pavimentacao = trecho.get("pavimentacao")
        estado = trecho.get("estado_pavimento")

        if not pavimentacao and not estado:
            continue

        observacoes = (
            f"MTD: {trecho.get('mtd_mm')} mm. "
            f"Origem: dados simulados."
        )

        cursor.execute(
            """
            INSERT INTO condicoes_pista (
                trecho_id,
                pavimentacao,
                estado_pavimento,
                observacoes
            )
            SELECT %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1
                FROM condicoes_pista
                WHERE trecho_id = %s
            )
            """,
            (
                trecho["id"],
                pavimentacao,
                estado,
                observacoes,
                trecho["id"],
            ),
        )

    print("Condições dos pavimentos importadas.")


def importar_drenagem(cursor, trechos):
    for trecho in trechos:
        dados = trecho.get("drenagem", {})

        if not dados:
            continue

        cursor.execute(
            """
            INSERT INTO drenagem (
                trecho_id,
                tipo,
                quantidade,
                capacidade_individual,
                capacidade_total
            )
            SELECT %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1
                FROM drenagem
                WHERE trecho_id = %s
            )
            """,
            (
                trecho["id"],
                dados.get("tipo"),
                dados.get("quantidade", 1),
                dados.get("capacidade_individual_l_s"),
                dados.get("capacidade_total_l_s"),
                trecho["id"],
            ),
        )

    print("Dados de drenagem importados.")


def main():
    trechos = carregar_trechos()

    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            importar_condicoes(cursor, trechos)
            importar_drenagem(cursor, trechos)

    print("Importação de pavimentos e drenagem concluída!")


if __name__ == "__main__":
    main()
