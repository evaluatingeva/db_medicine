# Search System using PostgreSQL
Click here to see the output of the system: 

Supports:

Prefix search (e.g., Ava → “Avastin”)
Substring search (e.g., Injection → “… Injection” items)
Full-text search (e.g., antibiotic)
Fuzzy (typo-tolerant) search using trigrams (e.g., Avastn → “Avastin”)

The Repo contains:
1. schema.sql (trigger-based normalization + all indexes)
2. import_data.py (loads all JSON files under data/)
3. app/ (FastAPI (REST APIs): /search/prefix, /search/substring, /search/fulltext, /search/fuzzy, alias /search/fussy)
4. benchmark/ (benchmark + submission generator)
5. Dockerfile.api and docker-compose.yml

Requirements: PostgreSQL, Python 3.10+, Docker desktop
# Procedure
1. Clone the Repo & Include the Dataset in the folder
2. Create the Database using ubuntu with the following commands:
   
    psql -U postgres -h localhost -c "CREATE DATABASE medicines;"
    
    psql -U postgres -h localhost -d medicines -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
    
    psql -U postgres -h localhost -d medicines -c "CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;"
    
    psql -U postgres -h localhost -d medicines -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
4. Now add the files and folders in the Clone Repo Folder.
5. Now using the "wsl Ubuntu commands: 
    1. Apply the schema
    2. Create the virtual environment (python venv) Activate it and install psycopg[binary] python-dotenv
    3. using export keyword make the connection to the local DB
    4. Import the JSON data by running python import_data.py
    5. Check using this cmd then:(psql -U postgres -h localhost -d medicines -c "SELECT count(*) FROM medicines;")
    6. Now Install the requirements from the app folder for FAST APIs to implement
    7. Then again run the export cmd.
    8. then run the application using this -> (uvicorn app.main:app --reload --port 8000)
    9. Now we open the following links:
        -> Swagger UI: http://127.0.0.1:8000/docs
       
        -> Prefix: http://127.0.0.1:8000/search/prefix?q=Ava
       
        -> Substr: http://127.0.0.1:8000/search/substring?q=Injection
       
        -> FTS: http://127.0.0.1:8000/search/fulltext?q=antibiotic
       
        -> Fuzzy: http://127.0.0.1:8000/search/fuzzy?q=Avastn&threshold=0.25
    11. Now run the benchmark.py and submission_gen.py files using: 
        python benchmark.py --host 127.0.0.1:8000 > benchmark_results.json
        python submission_gen.py --host 127.0.0.1:8000 --out ../submission.json
    # OUTPUT
    Created the benchmark_results.json file with latency and submission.json file with the required results format. (fixed query set)
    11. I have build the docker image, enabled teh extensions, applied the schema in the container database, imported teh data in the container database
So, this is how I successfully implemented the project!
