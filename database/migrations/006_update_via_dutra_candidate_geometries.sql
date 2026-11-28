-- Troca as geometrias de teste da Via Dutra pelas coordenadas candidatas
-- mais recentes fornecidas pelo usuario. Mantem validacao espacial pendente.
-- Aplicar depois das migrations 004 e 005.

BEGIN;

WITH data(codigo, geometria_wkt) AS (VALUES
    ('BR116-SP-225-226', 'LINESTRING(-46.57680 -23.51590,-46.58120 -23.51940,-46.58550 -23.52280)'),
    ('BR116-SP-226-227', 'LINESTRING(-46.58550 -23.52280,-46.58820 -23.52450,-46.59280 -23.52380)'),
    ('BR116-SP-227-228', 'LINESTRING(-46.59280 -23.52380,-46.59850 -23.52210,-46.60380 -23.52100)'),
    ('BR116-SP-228-229', 'LINESTRING(-46.60380 -23.52100,-46.60950 -23.52040,-46.61520 -23.51980)'),
    ('BR116-SP-229-230', 'LINESTRING(-46.61520 -23.51980,-46.62080 -23.51950,-46.62620 -23.51960)')
)
UPDATE trechos t SET
    geometria = ST_SetSRID(ST_GeomFromText(d.geometria_wkt), 4326),
    geometria_validada = FALSE,
    origem_geometria = 'Candidate coordinates supplied by user for mock testing; not spatially verified.'
FROM data d
WHERE t.codigo = d.codigo;

COMMIT;
