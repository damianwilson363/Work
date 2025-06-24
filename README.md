
# Drone Mapping Backend

FastAPI backend for drone-based pasture and weed analysis.

## Features
- Upload drone images
- Generate weed detection overlays
- Generate GeoJSON for map visualization
- Download KML for spray drones (DJI Agras compatible)
- Generate PDF reports

## Run Locally
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deployment (Render Example)
- Start command:
```bash
uvicorn app.main:app --host=0.0.0.0 --port=10000
```
