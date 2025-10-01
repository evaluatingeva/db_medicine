#!/usr/bin/env python3
import json, os, sys, glob, psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

"""
Loads *all* JSON files in ./data into the 'medicines' table.

Each JSON file can be a list of objects with fields:
id, sku_id, name, manufacturer_name, marketer_name, type, price,
pack_size_label, short_composition, is_discontinued, available
"""

def iter_json_files(folder):
    for p in glob.glob(os.path.join(folder, "*.json")):
        yield p

def records_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):   # if file contains an object with nested list
            # try to find the first list in the dict
            for v in data.values():
                if isinstance(v, list):
                    return v
            return []
        return data if isinstance(data, list) else []

def main():
    load_dotenv()
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("Set DATABASE_URL in .env or env vars.")
        sys.exit(1)

    data_dir = os.path.join(os.getcwd(), "data")
    files = list(iter_json_files(data_dir))
    if not files:
        print(f"No JSON files found under {data_dir}")
        sys.exit(1)

    total = 0
    sql = """
    INSERT INTO medicines(
      id, sku_id, name, manufacturer_name, marketer_name, type, price,
      pack_size_label, short_composition, is_discontinued, available
    )
    VALUES(
      %(id)s, %(sku_id)s, %(name)s, %(manufacturer_name)s, %(marketer_name)s, %(type)s, %(price)s,
      %(pack_size_label)s, %(short_composition)s, %(is_discontinued)s, %(available)s
    )
    ON CONFLICT (id) DO UPDATE SET
      sku_id = EXCLUDED.sku_id,
      name   = EXCLUDED.name,
      manufacturer_name = EXCLUDED.manufacturer_name,
      marketer_name     = EXCLUDED.marketer_name,
      type   = EXCLUDED.type,
      price  = EXCLUDED.price,
      pack_size_label = EXCLUDED.pack_size_label,
      short_composition = EXCLUDED.short_composition,
      is_discontinued = EXCLUDED.is_discontinued,
      available = EXCLUDED.available;
    """

    with psycopg.connect(dsn) as conn:
        conn.execute("SET application_name='import_data'")
        with conn.cursor(row_factory=dict_row) as cur:
            for fp in files:
                recs = records_from_file(fp)
                if not recs: 
                    continue
                batch, B = [], 1000
                for r in recs:
                    batch.append(r)
                    if len(batch) >= B:
                        cur.executemany(sql, batch); conn.commit(); total += len(batch); batch.clear()
                if batch:
                    cur.executemany(sql, batch); conn.commit(); total += len(batch)

    print(f"Imported/Upserted {total} rows from {len(files)} files.")

if __name__ == "__main__":
    main()
