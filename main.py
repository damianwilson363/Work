
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fpdf import FPDF
import geojson
import random
import io
import numpy as np
import cv2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Drone Mapping API is running."}

@app.post("/generate_geojson_fake/")
async def generate_geojson_fake(file: UploadFile = File(...)):
    # Return example weed patches for frontend map
    features = []
    for i in range(5):
        lon = 175.5 + random.uniform(-0.01, 0.01)
        lat = -40.3 + random.uniform(-0.01, 0.01)
        density = random.choice(["high", "medium", "low"])
        features.append(geojson.Feature(geometry=geojson.Point((lon, lat)), properties={"weed_density": density}))
    return geojson.FeatureCollection(features)

@app.post("/generate_spray_kml/")
async def generate_spray_kml(file: UploadFile = File(...)):
    example_points = [(175.5001, -40.3001), (175.5015, -40.2995), (175.5030, -40.2980)]
    kml = ['<?xml version="1.0" encoding="UTF-8"?>']
    kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml.append('<Document><name>Weed Spray Targets</name>')
    for lon, lat in example_points:
        kml.append(f'''
            <Placemark>
                <name>Weed Patch</name>
                <Point><coordinates>{lon},{lat},0</coordinates></Point>
            </Placemark>
        ''')
    kml.append('</Document></kml>')
    kml_str = '\n'.join(kml)
    return StreamingResponse(io.BytesIO(kml_str.encode()), media_type="application/vnd.google-earth.kml+xml",
                             headers={"Content-Disposition": "attachment; filename=weed_spray_targets.kml"})

@app.get("/generate_pdf_report/")
async def generate_pdf_report():
    class PDFReport(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Pasture & Weed Analysis Report", ln=True, align="C")

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

        def add_summary(self, pasture_vari, recommendation, weed_percentage, weed_recommendation, kml_link):
            self.set_font("Arial", "", 12)
            self.cell(0, 10, f"Average Pasture VARI: {pasture_vari}", ln=True)
            self.cell(0, 10, f"Grazing Recommendation: {recommendation}", ln=True)
            self.cell(0, 10, f"Weed Coverage: {weed_percentage}%", ln=True)
            self.cell(0, 10, f"Weed Control Recommendation: {weed_recommendation}", ln=True)
            self.cell(0, 10, f"KML Spray Map: {kml_link}", ln=True, link=kml_link)

    pdf = PDFReport()
    pdf.add_page()
    pdf.add_summary(
        pasture_vari=0.42,
        recommendation="Rest paddock (Improving growth)",
        weed_percentage=12.5,
        weed_recommendation="High weed cover - Spot spraying recommended",
        kml_link="http://127.0.0.1:8000/generate_spray_kml/"
    )
    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return StreamingResponse(pdf_bytes, media_type="application/pdf",
                             headers={"Content-Disposition": "attachment; filename=report.pdf"})
