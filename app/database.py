import os
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medicines")
pool = ConnectionPool(conninfo=DATABASE_URL, min_size=1, max_size=10, kwargs={"application_name":"api"})
