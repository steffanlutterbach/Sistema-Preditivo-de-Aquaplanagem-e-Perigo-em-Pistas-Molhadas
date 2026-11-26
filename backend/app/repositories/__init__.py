"""Repositórios com adaptadores para modo mock e PostgreSQL/PostGIS."""

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from threading import RLock
from typing import Any

from psycopg.types.json import Jsonb
from psycopg.errors import UniqueViolation

from app.core.config import ALERT_VALIDITY_MINUTES, DATA_MODE, METEOROLOGY_STALE_MINUTES
from app.core.database import conectar, verificar_conexao

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
MOCK_DIR = PROJECT_DIR / "mock_data"
_lock = RLock()
_rodovias_mem: list[dict[str, Any]] | None = None
_trechos_mem: list[dict[str, Any]] | None = None
_estacoes_mem: list[dict[str, Any]] | None = None
_medicoes: list[dict[str, Any]] = []
_analises: list[dict[str, Any]] = []
_alertas: list[dict[str, Any]] = []
_ids = {"trecho": 100, "medicao": 0, "analise": 0, "alerta": 0}


def _plain(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _real() -> bool:
    return DATA_MODE == "real"


def _ler_json(nome: str) -> Any:
    with (MOCK_DIR / nome).open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _as_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def dados_desatualizados(data_hora: Any) -> bool:
    measured_at = _as_datetime(data_hora)
    return measured_at is None or datetime.now(timezone.utc) - measured_at > timedelta(minutes=METEOROLOGY_STALE_MINUTES)


def _mem_rodovias() -> list[dict[str, Any]]:
    global _rodovias_mem
    with _lock:
        if _rodovias_mem is None:
            _rodovias_mem = _ler_json("rodovias.json")
        return _rodovias_mem


def _mem_trechos() -> list[dict[str, Any]]:
    global _trechos_mem
    with _lock:
        if _trechos_mem is None:
            _trechos_mem = _ler_json("trechos.json")
        return _trechos_mem


def _linha_trecho(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    if item.get("geometria") and isinstance(item["geometria"], str):
        item["geometria"] = json.loads(item["geometria"])
    item["inclinacao_percentual"] = item.pop("inclinacao", item.get("inclinacao_percentual"))
    return item


def listar_rodovias() -> list[dict[str, Any]]:
    if not _real():
        return [dict(item) for item in _mem_rodovias()]
    with conectar() as conn:
        return [_plain(dict(row)) for row in conn.execute("SELECT id,nome,estado,descricao FROM rodovias ORDER BY nome").fetchall()]


def listar_trechos() -> list[dict[str, Any]]:
    if not _real():
        return [dict(item) for item in _mem_trechos()]
    query = """
        SELECT t.id,t.codigo,t.rodovia_id,t.km_inicial,t.km_final,
               t.comprimento AS comprimento_m,t.largura AS largura_m,
               t.area_contribuicao_m2,t.coeficiente_escoamento,
               t.inclinacao AS inclinacao_percentual,t.mtd_mm,
               t.caminho_escoamento_m,t.declividade_caminho_pct AS declividade_caminho_percentual,
               t.estado_inclinacao,t.origem_geometria,t.geometria_validada,t.origem_dados,
               ST_AsGeoJSON(t.geometria)::json AS geometria,
               cp.pavimentacao,cp.estado_pavimento,
               dr.tipo AS drenagem_tipo,dr.quantidade AS drenagem_quantidade,
               dr.capacidade_individual AS drenagem_capacidade_individual_l_s,
               dr.capacidade_total AS drenagem_capacidade_total_l_s,dr.observacoes AS drenagem_observacao
        FROM trechos t
        LEFT JOIN LATERAL (SELECT pavimentacao,estado_pavimento FROM condicoes_pista
                           WHERE trecho_id=t.id ORDER BY data_inspecao DESC LIMIT 1) cp ON TRUE
        LEFT JOIN LATERAL (SELECT tipo,quantidade,capacidade_individual,capacidade_total FROM drenagem
                           WHERE trecho_id=t.id ORDER BY id DESC LIMIT 1) dr ON TRUE
        ORDER BY t.km_inicial NULLS LAST,t.id
    """
    with conectar() as conn:
        rows = conn.execute(query).fetchall()
    results = []
    for row in rows:
        item = _linha_trecho(row)
        item["drenagem"] = {
            "tipo": item.pop("drenagem_tipo", None),
            "quantidade": item.pop("drenagem_quantidade", None),
            "capacidade_individual_l_s": item.pop("drenagem_capacidade_individual_l_s", None),
            "capacidade_total_l_s": item.pop("drenagem_capacidade_total_l_s", None),
            "observacao": item.pop("drenagem_observacao", None),
        }
        results.append(_plain(item))
    return results


def consultar_trecho(trecho_id: int) -> dict[str, Any] | None:
    return next((item for item in listar_trechos() if int(item["id"]) == trecho_id), None)


def _salvar_caracteristicas(conn: Any, trecho_id: int, dados: dict[str, Any]) -> None:
    if dados.get("pavimentacao") or dados.get("estado_pavimento"):
        conn.execute("INSERT INTO condicoes_pista (trecho_id,pavimentacao,estado_pavimento,observacoes) VALUES (%s,%s,%s,%s)",
                     (trecho_id,dados.get("pavimentacao"),dados.get("estado_pavimento"),dados.get("observacoes")))
    drainage = dados.get("drenagem")
    if drainage:
        conn.execute("INSERT INTO drenagem (trecho_id,tipo,quantidade,capacidade_individual,capacidade_total,observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                     (trecho_id,drainage.get("tipo"),drainage.get("quantidade",1),
                      drainage.get("capacidade_individual_l_s"),drainage.get("capacidade_total_l_s"),
                      drainage.get("observacao")))


def criar_trecho(trecho: dict[str, Any]) -> dict[str, Any]:
    if not _real():
        with _lock:
            segments = _mem_trechos()
            if any(item.get("codigo") == trecho.get("codigo") for item in segments):
                raise ValueError("Já existe um trecho com esse código")
            item = dict(trecho)
            item["id"] = max((int(x["id"]) for x in segments), default=0) + 1
            item.setdefault("origem_dados", "mock")
            segments.append(item)
            return dict(item)
    geometry = trecho.get("geometria")
    try:
        with conectar() as conn:
            row = conn.execute(
            """INSERT INTO trechos (codigo,rodovia_id,km_inicial,km_final,comprimento,largura,
               area_contribuicao_m2,coeficiente_escoamento,inclinacao,geometria,
               mtd_mm,caminho_escoamento_m,declividade_caminho_pct,estado_inclinacao,origem_geometria,geometria_validada,origem_dados)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,
               CASE WHEN %s::jsonb IS NULL THEN NULL ELSE ST_SetSRID(ST_GeomFromGeoJSON(%s),4326) END,
               %s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (trecho.get("codigo"),trecho["rodovia_id"],trecho["km_inicial"],trecho["km_final"],
             trecho.get("comprimento_m"),trecho.get("largura_m"),trecho.get("area_contribuicao_m2"),
             trecho.get("coeficiente_escoamento"),trecho.get("inclinacao_percentual"),
             json.dumps(geometry) if geometry else None,json.dumps(geometry) if geometry else None,
             trecho.get("mtd_mm"),trecho.get("caminho_escoamento_m"),trecho.get("declividade_caminho_percentual"),
             trecho.get("estado_inclinacao"),trecho.get("origem_geometria"),
             trecho.get("geometria_validada",False),trecho.get("origem_dados","real")),
            ).fetchone()
            new_id = row["id"]
            _salvar_caracteristicas(conn,new_id,trecho)
    except UniqueViolation as erro:
        raise ValueError("Já existe um trecho com esse código") from erro
    return consultar_trecho(new_id) or {"id":new_id,**trecho}


def atualizar_trecho(trecho_id: int, alteracoes: dict[str, Any]) -> dict[str, Any] | None:
    current = consultar_trecho(trecho_id)
    if current is None:
        return None
    if not _real():
        with _lock:
            stored = next(item for item in _mem_trechos() if int(item["id"]) == trecho_id)
            stored.update(alteracoes)
            return dict(stored)
    columns = {"codigo":"codigo","rodovia_id":"rodovia_id","km_inicial":"km_inicial","km_final":"km_final",
        "comprimento_m":"comprimento","largura_m":"largura","area_contribuicao_m2":"area_contribuicao_m2",
        "coeficiente_escoamento":"coeficiente_escoamento","inclinacao_percentual":"inclinacao","mtd_mm":"mtd_mm",
        "caminho_escoamento_m":"caminho_escoamento_m","declividade_caminho_percentual":"declividade_caminho_pct",
        "estado_inclinacao":"estado_inclinacao","origem_geometria":"origem_geometria",
        "geometria_validada":"geometria_validada","origem_dados":"origem_dados"}
    changes = [(columns[k],v) for k,v in alteracoes.items() if k in columns]
    try:
        with conectar() as conn:
            if changes:
                assignments = ",".join(f"{column}=%s" for column,_ in changes)
                conn.execute(f"UPDATE trechos SET {assignments} WHERE id=%s",[v for _,v in changes]+[trecho_id])
            if alteracoes.get("geometria") is not None:
                conn.execute("UPDATE trechos SET geometria=ST_SetSRID(ST_GeomFromGeoJSON(%s),4326) WHERE id=%s",
                             (json.dumps(alteracoes["geometria"]),trecho_id))
            _salvar_caracteristicas(conn,trecho_id,alteracoes)
    except UniqueViolation as erro:
        raise ValueError("Já existe um trecho com esse código") from erro
    return consultar_trecho(trecho_id)


def listar_estacoes(trecho_id: int | None = None) -> list[dict[str, Any]]:
    if not _real():
        global _estacoes_mem
        with _lock:
            if _estacoes_mem is None:
                _estacoes_mem = _ler_json("estacoes.json")
            stations = [dict(s) for s in _estacoes_mem]
        if trecho_id is None:
            return stations
        associated = []
        for station in stations:
            if trecho_id in station.get("trechos_candidatos", []):
                item = dict(station)
                item.update(station.get("associacoes", {}).get(str(trecho_id), {}))
                item["trecho_id"] = trecho_id
                associated.append(item)
        return associated
    query = """SELECT e.id,e.codigo_externo,e.nome,e.ativa,e.origem_dados,te.trecho_id,
       te.status_associacao,te.distancia_km,fd.nome AS fonte
       FROM estacoes_meteorologicas e LEFT JOIN fontes_dados fd ON fd.id=e.fonte_id
       LEFT JOIN trechos_estacoes te ON te.estacao_id=e.id
       WHERE (%s::integer IS NULL OR te.trecho_id=%s) ORDER BY e.nome"""
    with conectar() as conn:
        return [_plain(dict(row)) for row in conn.execute(query,(trecho_id,trecho_id)).fetchall()]


def criar_estacao(dados: dict[str, Any]) -> dict[str, Any]:
    if _real():
        try:
          with conectar() as conn:
            source = conn.execute("""INSERT INTO fontes_dados(nome,tipo,descricao) VALUES (%s,'meteorologica',%s)
                ON CONFLICT(nome) DO UPDATE SET nome=EXCLUDED.nome RETURNING id""",
                (dados["fonte"],"Fonte configurada pelo operador do AquaSafe.")).fetchone()
            row = conn.execute("""INSERT INTO estacoes_meteorologicas(codigo_externo,fonte_id,nome,latitude,longitude,geometria,origem_dados,observacoes)
                VALUES (%s,%s,%s,%s,%s,CASE WHEN %s::double precision IS NULL OR %s::double precision IS NULL THEN NULL ELSE ST_SetSRID(ST_MakePoint(%s,%s),4326) END,%s,%s)
                RETURNING id,codigo_externo,nome,latitude,longitude,origem_dados,observacoes""",
                (dados["codigo_externo"],source["id"],dados["nome"],dados.get("latitude"),dados.get("longitude"),
                 dados.get("latitude"),dados.get("longitude"),dados.get("longitude"),dados.get("latitude"),
                 dados.get("origem_dados","real"),dados.get("observacoes"))).fetchone()
            return _plain(dict(row))
        except UniqueViolation as erro:
            raise ValueError("Já existe uma estação com esse código nesta fonte") from erro
    global _estacoes_mem
    with _lock:
        if _estacoes_mem is None:
            _estacoes_mem = _ler_json("estacoes.json")
        if any(s["codigo_externo"] == dados["codigo_externo"] for s in _estacoes_mem):
            raise ValueError("Já existe uma estação com esse código")
        item = {**dados, "id": max((s["id"] for s in _estacoes_mem), default=0) + 1,
                "trechos_candidatos": [], "status_associacao": "pendente_validacao"}
        _estacoes_mem.append(item)
        return dict(item)


def associar_estacao(trecho_id: int, estacao_id: int, dados: dict[str, Any]) -> dict[str, Any] | None:
    station = next((s for s in listar_estacoes() if s.get("id") == estacao_id), None)
    if station is None:
        return None
    if _real():
        with conectar() as conn:
            row = conn.execute("""INSERT INTO trechos_estacoes(trecho_id,estacao_id,status_associacao,distancia_km,justificativa)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT(trecho_id,estacao_id) DO UPDATE SET
                status_associacao=EXCLUDED.status_associacao,distancia_km=EXCLUDED.distancia_km,
                justificativa=EXCLUDED.justificativa RETURNING trecho_id,estacao_id,status_associacao,distancia_km,justificativa""",
                (trecho_id,estacao_id,dados.get("status_associacao","pendente_validacao"),
                 dados.get("distancia_km"),dados.get("justificativa"))).fetchone()
            return _plain(dict(row))
    global _estacoes_mem
    with _lock:
        if _estacoes_mem is None:
            _estacoes_mem = _ler_json("estacoes.json")
        target = next(s for s in _estacoes_mem if s["id"] == estacao_id)
        candidates = target.setdefault("trechos_candidatos", [])
        if trecho_id not in candidates:
            candidates.append(trecho_id)
        target.setdefault("associacoes", {})[str(trecho_id)] = dados
        return {"trecho_id":trecho_id,"estacao_id":estacao_id,**dados}


def listar_cenarios() -> list[dict[str, Any]]:
    return _ler_json("cenarios_chuva.json")["cenarios"]


def listar_medicoes(trecho_id: int | None = None) -> list[dict[str, Any]]:
    if _real():
        with conectar() as conn:
            rows = conn.execute("""SELECT dm.id,dm.trecho_id,fd.nome AS fonte,dm.modo_dados,
                dm.precipitacao AS precipitacao_mm,dm.intensidade_chuva AS intensidade_mm_h,
                dm.data_hora,dm.estacao_id,dm.identificador_externo
                FROM dados_meteorologicos dm LEFT JOIN fontes_dados fd ON fd.id=dm.fonte_id
                WHERE (%s::integer IS NULL OR dm.trecho_id=%s) ORDER BY dm.data_hora DESC""",(trecho_id,trecho_id)).fetchall()
        items = [_plain(dict(row)) for row in rows]
    else:
        with _lock:
            items = [dict(item) for item in _medicoes]
        items = [item for item in items if trecho_id is None or item["trecho_id"] == trecho_id]
        items.sort(key=lambda item:str(item.get("data_hora","")),reverse=True)
    for item in items:
        item["dados_desatualizados"] = dados_desatualizados(item.get("data_hora"))
        if isinstance(item.get("data_hora"),datetime):
            item["data_hora"] = item["data_hora"].isoformat()
    return items


def registrar_medicao(medicao: dict[str, Any]) -> dict[str, Any]:
    for existing in listar_medicoes(medicao["trecho_id"]):
        if existing.get("fonte") == medicao.get("fonte") and _as_datetime(existing.get("data_hora")) == _as_datetime(medicao.get("data_hora")):
            raise ValueError("Medição duplicada para trecho, fonte e data/hora")
    item = dict(medicao)
    item.setdefault("modo_dados","real" if _real() else "mock")
    if _real():
        try:
          with conectar() as conn:
            source = conn.execute("""INSERT INTO fontes_dados (nome,tipo,descricao) VALUES (%s,'meteorologica',%s)
                ON CONFLICT (nome) DO UPDATE SET nome=EXCLUDED.nome RETURNING id""",
                (item.get("fonte","desconhecida"),"Fonte declarada pelo produtor da medição.")).fetchone()
            row = conn.execute("""INSERT INTO dados_meteorologicos (trecho_id,fonte_id,precipitacao,
                intensidade_chuva,data_hora,estacao_id,modo_dados,identificador_externo)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (item["trecho_id"],source["id"],item.get("precipitacao_mm"),item.get("intensidade_mm_h"),
                 _as_datetime(item["data_hora"]),item.get("estacao_id"),item["modo_dados"],item.get("identificador_externo"))).fetchone()
            item["id"] = row["id"]
        except UniqueViolation as erro:
            raise ValueError("Medição duplicada para trecho, fonte, data/hora ou identificador externo") from erro
    else:
        with _lock:
            for existing in _medicoes:
                if existing["trecho_id"] == item["trecho_id"] and existing.get("fonte") == item.get("fonte") and _as_datetime(existing.get("data_hora")) == _as_datetime(item.get("data_hora")):
                    raise ValueError("Medição duplicada para trecho, fonte e data/hora")
            _ids["medicao"] += 1
            item["id"] = _ids["medicao"]
            _medicoes.append(item)
    item["data_hora"] = item["data_hora"].isoformat() if isinstance(item["data_hora"],datetime) else item["data_hora"]
    item["dados_desatualizados"] = dados_desatualizados(item.get("data_hora"))
    return item


def obter_medicao_recente(trecho_id: int) -> dict[str, Any] | None:
    items = listar_medicoes(trecho_id)
    return items[0] if items else None


def listar_analises(trecho_id: int | None = None) -> list[dict[str, Any]]:
    if _real():
        with conectar() as conn:
            rows = conn.execute("""SELECT id,trecho_id,dados_clima_id,vazao_estimada AS vazao_estimada_l_s,
                volume_acumulado AS volume_acumulado_l,pontuacao_risco,nivel_risco,data_analise,
                status_analise,dados_utilizados,versao_algoritmo,origem_dados,dados_ausentes,
                dados_desatualizados,wd_mm FROM analises_risco WHERE (%s::integer IS NULL OR trecho_id=%s)
                ORDER BY data_analise DESC""",(trecho_id,trecho_id)).fetchall()
        return [_plain(dict(row)) for row in rows]
    with _lock:
        items = [dict(item) for item in _analises]
    return sorted([i for i in items if trecho_id is None or i["trecho_id"]==trecho_id],key=lambda i:i.get("id",0),reverse=True)


def registrar_analise(analise: dict[str, Any]) -> dict[str, Any]:
    item = dict(analise)
    if _real():
        with conectar() as conn:
            row = conn.execute("""INSERT INTO analises_risco (trecho_id,dados_clima_id,vazao_estimada,
                volume_acumulado,pontuacao_risco,nivel_risco,data_analise,status_analise,dados_utilizados,
                versao_algoritmo,origem_dados,dados_ausentes,dados_desatualizados,wd_mm)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (item["trecho_id"],item["dados_clima_id"],item.get("vazao_estimada_l_s"),item.get("volume_acumulado_l"),
                 item.get("pontuacao_risco"),item.get("nivel_risco"),_as_datetime(item["data_analise"]),item["status_analise"],
                 Jsonb(item["dados_utilizados"]),item["versao_algoritmo"],item["origem_dados"],item["dados_ausentes"],
                 item["dados_desatualizados"],item.get("wd_mm"))).fetchone()
            item["id"] = row["id"]
    else:
        with _lock:
            _ids["analise"] += 1
            item["id"] = _ids["analise"]
            _analises.append(item)
    return item


def _expirar_alertas_mock() -> None:
    now = datetime.now(timezone.utc)
    for item in _alertas:
        expiry = _as_datetime(item.get("validade"))
        if item.get("status")=="ativo" and expiry and expiry<=now:
            item["status"]="expirado"


def sincronizar_alerta(analise: dict[str, Any]) -> dict[str, Any] | None:
    trecho_id,nivel=analise["trecho_id"],analise.get("nivel_risco")
    key=f"trecho:{trecho_id}"
    now=_as_datetime(analise["data_analise"]) or datetime.now(timezone.utc)
    expiry=now+timedelta(minutes=ALERT_VALIDITY_MINUTES)
    if _real():
        with conectar() as conn:
            conn.execute("UPDATE alertas SET status='expirado' WHERE status='ativo' AND validade IS NOT NULL AND validade<=now()")
            existing=conn.execute("""SELECT a.id,a.nivel,a.mensagem,a.status,a.data_hora,a.validade,a.chave_deduplicacao
                FROM alertas a JOIN analises_risco ar ON ar.id=a.analise_id
                WHERE ar.trecho_id=%s AND a.status='ativo' ORDER BY a.data_hora DESC LIMIT 1""",(trecho_id,)).fetchone()
            if nivel not in {"moderado","alto"}:
                if existing: conn.execute("UPDATE alertas SET status='resolvido' WHERE id=%s",(existing["id"],))
                return None
            if existing and existing["nivel"]==nivel:
                conn.execute("UPDATE alertas SET validade=%s WHERE id=%s",(expiry,existing["id"]))
                existing["validade"]=expiry
                result = dict(existing)
                result["chave_notificacao"] = f"aqua-alerta:{existing['id']}:{nivel}"
                return _plain(result)
            if existing: conn.execute("UPDATE alertas SET status='resolvido' WHERE id=%s",(existing["id"],))
            message=f"AquaSafe: risco {nivel} de aquaplanagem no segmento {trecho_id}. Reduza a velocidade com segurança e redobre a atenção."
            row=conn.execute("""INSERT INTO alertas (analise_id,nivel,mensagem,status,data_hora,validade,chave_deduplicacao)
                VALUES (%s,%s,%s,'ativo',%s,%s,%s) RETURNING id,nivel,mensagem,status,data_hora,validade,chave_deduplicacao""",
                (analise["id"],nivel,message,now,expiry,key)).fetchone()
            result = dict(row)
            result["chave_notificacao"] = f"aqua-alerta:{row['id']}:{nivel}"
            return _plain(result)
    with _lock:
        _expirar_alertas_mock()
        existing=next((a for a in reversed(_alertas) if a["trecho_id"]==trecho_id and a["status"]=="ativo"),None)
        if nivel not in {"moderado","alto"}:
            if existing: existing["status"]="resolvido"
            return None
        if existing and existing["nivel"]==nivel:
            existing["validade"]=expiry.isoformat()
            result = dict(existing)
            result["chave_notificacao"] = f"aqua-alerta:{existing['id']}:{nivel}"
            return result
        if existing: existing["status"]="resolvido"
        _ids["alerta"]+=1
        item={"id":_ids["alerta"],"trecho_id":trecho_id,"analise_id":analise["id"],"nivel":nivel,
              "mensagem":f"AquaSafe: risco {nivel} de aquaplanagem no segmento {trecho_id}. Reduza a velocidade com segurança e redobre a atenção.",
              "status":"ativo","data_hora":now.isoformat(),"validade":expiry.isoformat(),"chave_deduplicacao":key}
        _alertas.append(item)
        return dict(item)


def listar_alertas(trecho_id: int | None = None, historico: bool = False) -> list[dict[str, Any]]:
    if _real():
        with conectar() as conn:
            conn.execute("UPDATE alertas SET status='expirado' WHERE status='ativo' AND validade IS NOT NULL AND validade<=now()")
            rows=conn.execute("""SELECT a.id,ar.trecho_id,a.analise_id,a.nivel,a.mensagem,a.status,a.data_hora,
                a.validade,a.chave_deduplicacao,ar.pontuacao_risco,ar.versao_algoritmo
                FROM alertas a JOIN analises_risco ar ON ar.id=a.analise_id
                WHERE (%s OR a.status='ativo') AND (%s::integer IS NULL OR ar.trecho_id=%s) ORDER BY a.data_hora DESC""",
                (historico,trecho_id,trecho_id)).fetchall()
        return [_plain({**dict(row), "chave_notificacao": f"aqua-alerta:{row['id']}:{row['nivel']}"}) for row in rows]
    with _lock:
        _expirar_alertas_mock()
        items=[dict(item) for item in _alertas]
    result = [i for i in items if (historico or i["status"]=="ativo") and (trecho_id is None or i["trecho_id"]==trecho_id)]
    for item in result:
        item["chave_notificacao"] = f"aqua-alerta:{item['id']}:{item['nivel']}"
    return result


def verificar_banco() -> bool:
    return verificar_conexao()


def resetar_mock() -> None:
    global _rodovias_mem,_trechos_mem,_estacoes_mem
    with _lock:
        _rodovias_mem=None
        _trechos_mem=None
        _estacoes_mem=None
        _medicoes.clear(); _analises.clear(); _alertas.clear()
        for key in _ids: _ids[key]=0 if key!="trecho" else 100
