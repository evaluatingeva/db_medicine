from fastapi import FastAPI, Query
from app.database import pool
from app.models import SearchResponse
from app.search import PREFIX_SQL, SUBSTRING_SQL, FULLTEXT_SQL, FUZZY_SQL

app = FastAPI(title="Medicine Search API", version="1.0")
DEFAULT_LIMIT = 25

@app.get("/search/prefix", response_model=SearchResponse)
def prefix(q: str = Query(..., min_length=1), limit: int = DEFAULT_LIMIT):
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(PREFIX_SQL, (q, limit))
        rows = cur.fetchall()
    return SearchResponse(items=[r[0] for r in rows])

@app.get("/search/substring", response_model=SearchResponse)
def substring(q: str = Query(..., min_length=1), limit: int = DEFAULT_LIMIT):
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(SUBSTRING_SQL, (q, q, q, q, limit))
        rows = cur.fetchall()
    return SearchResponse(items=[r[0] for r in rows])

@app.get("/search/fulltext", response_model=SearchResponse)
def fulltext(q: str = Query(..., min_length=1), limit: int = DEFAULT_LIMIT):
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(FULLTEXT_SQL, (q, q, limit))
        rows = cur.fetchall()
    return SearchResponse(items=[r[0] for r in rows])

@app.get("/search/fuzzy", response_model=SearchResponse)
def fuzzy(q: str = Query(..., min_length=1), limit: int = DEFAULT_LIMIT, threshold: float = 0.25):
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(FUZZY_SQL, (q, threshold, q, limit))
        rows = cur.fetchall()
    return SearchResponse(items=[r[0] for r in rows])

# Alias for the brief's "fussy"
@app.get("/search/fussy", response_model=SearchResponse)
def fussy(q: str = Query(..., min_length=1), limit: int = DEFAULT_LIMIT, threshold: float = 0.25):
    return fuzzy(q=q, limit=limit, threshold=threshold)
