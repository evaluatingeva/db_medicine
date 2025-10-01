#!/usr/bin/env python3
import json, argparse, http.client, urllib.parse

def call(host, path):
    conn = http.client.HTTPConnection(host, timeout=10)
    conn.request("GET", path)
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    if resp.status != 200:
        raise RuntimeError(f"{path} -> HTTP {resp.status}")
    return json.loads(data.decode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost:8000")
    ap.add_argument("--queries", default="benchmark_queries.json")
    ap.add_argument("--out", default="submission.json")
    args = ap.parse_args()

    with open(args.queries, "r", encoding="utf-8") as f:
        qset = json.load(f)

    def path_of(q):
        t, s = q["type"], urllib.parse.quote(q["q"])
        if t == "prefix":    return f"/search/prefix?q={s}&limit=25"
        if t == "substring": return f"/search/substring?q={s}&limit=25"
        if t == "fulltext":  return f"/search/fulltext?q={s}&limit=25"
        if t == "fuzzy":     return f"/search/fuzzy?q={s}&limit=25&threshold=0.25"
        raise ValueError(t)

    results = {}
    for k, q in qset.items():
        out = call(args.host, path_of(q))
        results[k] = out["items"]

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
