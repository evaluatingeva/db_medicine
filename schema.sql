CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Start clean if previous attempt failed mid-way
DROP TABLE IF EXISTS medicines CASCADE;

-- NOTE: norm/tsv are plain columns (NOT generated), we'll maintain them via trigger.
CREATE TABLE medicines (
  id                BIGINT PRIMARY KEY,
  sku_id            TEXT,
  name              TEXT NOT NULL,
  manufacturer_name TEXT,
  marketer_name     TEXT,
  type              TEXT,
  price             NUMERIC,
  pack_size_label   TEXT,
  short_composition TEXT,
  is_discontinued   BOOLEAN,
  available         BOOLEAN,

  -- normalized copies (lower + unaccent)
  name_norm   TEXT,
  type_norm   TEXT,
  manuf_norm  TEXT,
  market_norm TEXT,
  comp_norm   TEXT,

  -- full-text vector
  tsv TSVECTOR
);

-- Trigger function to keep normalized/text-search columns updated
CREATE OR REPLACE FUNCTION medicines_normalize() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.name_norm   := unaccent(lower(coalesce(NEW.name,'')));
  NEW.type_norm   := unaccent(lower(coalesce(NEW.type,'')));
  NEW.manuf_norm  := unaccent(lower(coalesce(NEW.manufacturer_name,'')));
  NEW.market_norm := unaccent(lower(coalesce(NEW.marketer_name,'')));
  NEW.comp_norm   := unaccent(lower(coalesce(NEW.short_composition,'')));

  NEW.tsv := 
    setweight(to_tsvector('simple', unaccent(lower(coalesce(NEW.name,'')))), 'A') ||
    setweight(to_tsvector('simple', unaccent(lower(coalesce(NEW.type,'')))), 'B') ||
    setweight(to_tsvector('simple', unaccent(lower(coalesce(NEW.manufacturer_name,'')))), 'C') ||
    setweight(to_tsvector('simple', unaccent(lower(coalesce(NEW.short_composition,'')))), 'C');

  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_medicines_normalize ON medicines;
CREATE TRIGGER trg_medicines_normalize
BEFORE INSERT OR UPDATE ON medicines
FOR EACH ROW EXECUTE FUNCTION medicines_normalize();

-- Indexes
CREATE INDEX IF NOT EXISTS medicines_id_idx ON medicines (id);

-- Trigram GIN for prefix/substring
CREATE INDEX IF NOT EXISTS medicines_name_trgm_gin
  ON medicines USING GIN (name_norm gin_trgm_ops);
CREATE INDEX IF NOT EXISTS medicines_type_trgm_gin
  ON medicines USING GIN (type_norm gin_trgm_ops);
CREATE INDEX IF NOT EXISTS medicines_manuf_trgm_gin
  ON medicines USING GIN (manuf_norm gin_trgm_ops);
CREATE INDEX IF NOT EXISTS medicines_comp_trgm_gin
  ON medicines USING GIN (comp_norm gin_trgm_ops);

-- Full-text
CREATE INDEX IF NOT EXISTS medicines_tsv_gin
  ON medicines USING GIN (tsv);

CREATE INDEX IF NOT EXISTS medicines_available_idx ON medicines (available);
CREATE INDEX IF NOT EXISTS medicines_is_discontinued_idx ON medicines (is_discontinued);