-- 004: traçado dos 5 trechos mock acompanhando a pista
-- (Av. Prof. Francisco Morato -> Rod. Régis Bittencourt, de Vila Sônia até o centro de Taboão da Serra).
-- Mantém o início do trecho 1 e o fim do trecho 5 do seed 003; só a geometria passa a seguir a via
-- (antes eram retas entre dois pontos, que ficavam até ~500 m fora da pista no mapa).
-- Traçado digitalizado sobre o mapa do OpenStreetMap (© colaboradores do OpenStreetMap, licença ODbL).
-- Continua aproximado e NÃO validado oficialmente: geometria_validada permanece FALSE.
-- Mesmo conteúdo de mock_data/trechos.json. Aplicar depois da 003:
--   psql -U aquasafe -d aquasafe -f database/migrations/004_tracado_trechos_br116.sql

UPDATE trechos t
SET geometria = ST_GeomFromText(v.wkt, 4326),
    origem_geometria = 'Traçado aproximado sobre a via (digitalizado do OpenStreetMap); não validado oficialmente.'
FROM (VALUES
  ('BR116-264',
   'LINESTRING(-46.734133 -23.593111, -46.734722 -23.593294, -46.735241 -23.593503, -46.736776 -23.594333, -46.738142 -23.594942, -46.738538 -23.595195, -46.738836 -23.595439, -46.739344 -23.596030)'),
  ('BR116-265',
   'LINESTRING(-46.739344 -23.596030, -46.739709 -23.596652, -46.740449 -23.598259, -46.740873 -23.599001, -46.741529 -23.599794, -46.742597 -23.600786)'),
  ('BR116-266',
   'LINESTRING(-46.742597 -23.600786, -46.743389 -23.601513, -46.743928 -23.602094, -46.744329 -23.602659, -46.744944 -23.603802, -46.745236 -23.604258, -46.745713 -23.604794, -46.746297 -23.605273)'),
  ('BR116-267',
   'LINESTRING(-46.746297 -23.605273, -46.746776 -23.605584, -46.747356 -23.605891, -46.747871 -23.606105, -46.748325 -23.606240, -46.748956 -23.606338, -46.750375 -23.606325, -46.750995 -23.606417, -46.751467 -23.606657, -46.751950 -23.607073)'),
  ('BR116-268',
   'LINESTRING(-46.751950 -23.607073, -46.752530 -23.607651, -46.752906 -23.607957, -46.753391 -23.608230, -46.753914 -23.608433, -46.754946 -23.608696, -46.755929 -23.608866, -46.756763 -23.608928, -46.757552 -23.608895)')
) AS v(codigo, wkt)
WHERE t.codigo = v.codigo AND t.origem_dados = 'mock' AND t.geometria_validada = FALSE;
