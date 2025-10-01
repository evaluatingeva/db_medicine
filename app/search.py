PREFIX_SQL = """
SELECT name
FROM medicines
WHERE name_norm LIKE unaccent(lower(%s)) || '%%'
ORDER BY name
LIMIT %s;
"""

SUBSTRING_SQL = """
SELECT name
FROM medicines
WHERE name_norm ILIKE '%%' || unaccent(lower(%s)) || '%%'
   OR type_norm ILIKE '%%' || unaccent(lower(%s)) || '%%'
   OR manuf_norm ILIKE '%%' || unaccent(lower(%s)) || '%%'
   OR comp_norm ILIKE '%%' || unaccent(lower(%s)) || '%%'
ORDER BY name
LIMIT %s;
"""

FULLTEXT_SQL = """
SELECT name
FROM medicines
WHERE tsv @@ plainto_tsquery('simple', unaccent(lower(%s)))
ORDER BY ts_rank(tsv, plainto_tsquery('simple', unaccent(lower(%s)))) DESC, name
LIMIT %s;
"""

FUZZY_SQL = """
SELECT name
FROM medicines
WHERE similarity(name_norm, unaccent(lower(%s))) > %s
ORDER BY similarity(name_norm, unaccent(lower(%s))) DESC, name
LIMIT %s;
"""
