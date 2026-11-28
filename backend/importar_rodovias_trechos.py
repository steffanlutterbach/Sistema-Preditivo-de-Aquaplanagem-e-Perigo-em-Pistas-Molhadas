
import json
from pathlib import Path

from database import conectar_banco

# Localiza a pasta principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_DIR = BASE_DIR / "mock_data"


def carregar_json(nome_arquivo):
    caminho = MOCK_DIR / nome_arquivo

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def importar_rodovias(cursor):
    rodovias = carregar_json("rodovias.json")

    for rodovia in rodovias:
        cursor.execute(
            """
            INSERT INTO rodovias (id, nome, estado, descricao)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                nome = EXCLUDED.nome,
                estado = EXCLUDED.estado,
                descricao = EXCLUDED.descricao
            """,
            (
                rodovia["id"],
                rodovia["nome"],
                rodovia["estado"],
                rodovia.get("descricao"),
            ),
        )

    print(f"{len(rodovias)} rodovia(s) importada(s).")


def importar_trechos(cursor):
    trechos = carregar_json("trechos.json")

    for trecho in trechos:
        geometria = trecho.get("geometria")

        wkt = None

        if geometria and geometria.get("coordinates"):
            coordenadas = geometria["coordinates"]

            pontos = ", ".join(
                f"{longitude} {latitude}"
                for longitude, latitude in coordenadas
            )

            wkt = f"LINESTRING({pontos})"

        cursor.execute(
            """
            INSERT INTO trechos (
                id,
                rodovia_id,
                codigo,
                km_inicial,
                km_final,
                comprimento,
                largura,
                area_contribuicao_m2,
                coeficiente_escoamento,
                inclinacao,
                mtd_mm,
                caminho_escoamento_m,
                estado_inclinacao,
                declividade_caminho_percentual,
                geometria
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_GeomFromText(%s), 4326)
            )
            ON CONFLICT (id) DO UPDATE SET
                rodovia_id = EXCLUDED.rodovia_id,
                codigo = EXCLUDED.codigo,
                km_inicial = EXCLUDED.km_inicial,
                km_final = EXCLUDED.km_final,
                comprimento = EXCLUDED.comprimento,
                largura = EXCLUDED.largura,
                area_contribuicao_m2 = EXCLUDED.area_contribuicao_m2,
                coeficiente_escoamento = EXCLUDED.coeficiente_escoamento,
                inclinacao = EXCLUDED.inclinacao,
                mtd_mm = EXCLUDED.mtd_mm,
                caminho_escoamento_m = EXCLUDED.caminho_escoamento_m,
                estado_inclinacao = EXCLUDED.estado_inclinacao,
                declividade_caminho_percentual =
                    EXCLUDED.declividade_caminho_percentual,
                geometria = EXCLUDED.geometria
            """,
            (
                trecho["id"],
                trecho["rodovia_id"],
                trecho.get("codigo"),
                trecho.get("km_inicial"),
                trecho.get("km_final"),
                trecho.get("comprimento_m"),
                trecho.get("largura_m"),
                trecho.get("area_contribuicao_m2"),
                trecho.get("coeficiente_escoamento"),
                trecho.get("inclinacao_percentual"),
                trecho.get("mtd_mm"),
                trecho.get("caminho_escoamento_m"),
                trecho.get("estado_inclinacao"),
                trecho.get("declividade_caminho_percentual"),
                wkt,
            ),
        )

    print(f"{len(trechos)} trecho(s) importado(s).")


def ajustar_sequencias(cursor):
    for tabela in ("rodovias", "trechos"):
        cursor.execute(
            """
            SELECT setval(
                pg_get_serial_sequence(%s, 'id'),
                COALESCE((SELECT MAX(id) FROM """
            + tabela
            + """), 1),
                EXISTS (SELECT 1 FROM """
            + tabela
            + """)
            )
            """,
            (f"public.{tabela}",),
        )


def main():
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            importar_rodovias(cursor)
            importar_trechos(cursor)
            ajustar_sequencias(cursor)

    print("Importação concluída com sucesso!")


if __name__ == "__main__":
    main()
