#!/usr/bin/env python3
import time, json, argparse, statistics, http.client, urllib.parse

def request(host, path):
    conn = http.client.HTTPConnection(host, timeout=10)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    return resp.status, body

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost:8000")
    ap.add_argument("--queries", default="benchmark_queries.json")
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--runs", type=int, default=10)
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

    for _ in range(args.warmup):
        for _, q in qset.items():
            request(args.host, path_of(q))

    results = {}
    for k, q in qset.items():
        lat = []
        for _ in range(args.runs):
            t0 = time.perf_counter()
            status, _ = request(args.host, path_of(q))
            t1 = time.perf_counter()
            if status != 200:
                print(f"Non-200 on {k}: {status}")
            lat.append((t1 - t0) * 1000.0)
        lat.sort()
        results[k] = {
            "p50_ms": statistics.median(lat),
            "avg_ms": sum(lat)/len(lat),
            "p95_ms": lat[int(0.95*len(lat))-1]
        }
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
