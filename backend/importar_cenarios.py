
import json
from pathlib import Path

from database import conectar_banco

BASE_DIR = Path(__file__).resolve().parent.parent
ARQUIVO_CENARIOS = BASE_DIR / "mock_data" / "cenarios_chuva.json"


def carregar_cenarios():
    with open(ARQUIVO_CENARIOS, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados["cenarios"]


def importar_cenarios(cursor, cenarios):
    for cenario in cenarios:
        drenagem = cenario.get("drenagem", {})

        cursor.execute(
            """
            INSERT INTO cenarios_chuva (
                id,
                nome,
                trecho_id,
                fonte,
                precipitacao_mm,
                intensidade_mm_h,
                data_hora,
                estado_pavimento,
                quantidade_drenagem,
                capacidade_individual_l_s,
                capacidade_total_l_s,
                risco_esperado
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (id) DO UPDATE SET
                nome = EXCLUDED.nome,
                trecho_id = EXCLUDED.trecho_id,
                fonte = EXCLUDED.fonte,
                precipitacao_mm = EXCLUDED.precipitacao_mm,
                intensidade_mm_h = EXCLUDED.intensidade_mm_h,
                data_hora = EXCLUDED.data_hora,
                estado_pavimento = EXCLUDED.estado_pavimento,
                quantidade_drenagem = EXCLUDED.quantidade_drenagem,
                capacidade_individual_l_s =
                    EXCLUDED.capacidade_individual_l_s,
                capacidade_total_l_s = EXCLUDED.capacidade_total_l_s,
                risco_esperado = EXCLUDED.risco_esperado
            """,
            (
                cenario["id"],
                cenario["nome"],
                cenario["trecho_id"],
                cenario.get("fonte", "MOCK_LOCAL"),
                cenario.get("precipitacao_mm"),
                cenario.get("intensidade_mm_h"),
                cenario.get("data_hora"),
                cenario.get("estado_pavimento"),
                drenagem.get("quantidade"),
                drenagem.get("capacidade_individual_l_s"),
                drenagem.get("capacidade_total_l_s"),
                cenario.get("risco_esperado"),
            ),
        )

    print(f"{len(cenarios)} cenário(s) importado(s).")


def ajustar_sequencia(cursor):
    cursor.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('public.cenarios_chuva', 'id'),
            COALESCE((SELECT MAX(id) FROM cenarios_chuva), 1),
            EXISTS (SELECT 1 FROM cenarios_chuva)
        );
        """
    )


def main():
    cenarios = carregar_cenarios()

    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            importar_cenarios(cursor, cenarios)
            ajustar_sequencia(cursor)

    print("Importação dos cenários concluída!")


if __name__ == "__main__":
    main()
