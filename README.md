# NASA NEO Dashboard - Backend

API FastAPI per ottenere asteroidi Near Earth dalla NASA NeoWs.

## Endpoint
- `GET /asteroids?start_date=...&end_date=...` – lista asteroidi (supporta intervalli >7 giorni con chunking)
- `GET /asteroid/{id}` – dettaglio asteroide

## Deploy live
[https://nasa-backend-production-b2e2.up.railway.app](https://nasa-backend-production-b2e2.up.railway.app)

## Esecuzione locale
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload