from fastapi import FastAPI, Query
import requests
import os
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
if not NASA_API_KEY:
    raise Exception("Manca la chiave NASA. Imposta la variabile d'ambiente NASA_API_KEY.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = {}

@app.get("/asteroids")
def get_asteroids(start_date: str, end_date: str, refresh: bool = False):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return {"error": "Formato data non valido. Usa YYYY-MM-DD"}
    if start > end:
        return {"error": "start_date deve essere precedente a end_date"}
    
    if (end - start).days <= 7:
        cache_key = f"{start_date}_{end_date}"
        if not refresh and cache_key in cache:
            return cache[cache_key]
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
        data = requests.get(url).json()
        cache[cache_key] = data
        return data
    
    # chunking per intervalli lunghi
    current = start
    chunks = []
    while current <= end:
        chunk_end = min(current + timedelta(days=6), end)
        chunks.append((current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        current = chunk_end + timedelta(days=1)
    
    aggregated = {"near_earth_objects": {}}
    total = 0
    for cs, ce in chunks:
        cache_key = f"{cs}_{ce}"
        if not refresh and cache_key in cache:
            chunk_data = cache[cache_key]
        else:
            url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={cs}&end_date={ce}&api_key={NASA_API_KEY}"
            chunk_data = requests.get(url).json()
            cache[cache_key] = chunk_data
        for date, asteroids in chunk_data["near_earth_objects"].items():
            if date not in aggregated["near_earth_objects"]:
                aggregated["near_earth_objects"][date] = []
            aggregated["near_earth_objects"][date].extend(asteroids)
        total += chunk_data["element_count"]
    aggregated["element_count"] = total
    return aggregated

@app.get("/asteroid/{asteroid_id}")
def get_asteroid_details(asteroid_id: str, refresh: bool = Query(False)):
    cache_key = f"neo_{asteroid_id}"
    if not refresh and cache_key in cache:
        return cache[cache_key]
    url = f"https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={NASA_API_KEY}"
    data = requests.get(url).json()
    cache[cache_key] = data
    return data

@app.get("/")
def root():
    return {"message": "NASA NEO Dashboard API"}