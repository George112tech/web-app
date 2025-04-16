from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil, os, uuid
from report_utils import process_reports, validate_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ManualInputs(BaseModel):
    form: str
    term: str
    year: str
    vacation_date: str
    reopening_date: str
    number_on_roll: int
    report_format: str

@app.post("/upload-template")
def upload_template(template: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/template.docx"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(template.file, buffer)
    return {"message": "Template uploaded", "path": path}

@app.post("/upload-data")
def upload_data(data: UploadFile = File(...)):
    ext = data.filename.split(".")[-1]
    path = f"{UPLOAD_DIR}/data.{ext}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(data.file, buffer)
    return {"message": "Data uploaded", "path": path}

@app.post("/validate")
def validate():
    result = validate_data()
    return JSONResponse(content=result)

@app.post("/generate-reports")
def generate_reports(inputs: ManualInputs):
    zip_path = process_reports(inputs)
    return {"message": "Reports generated", "download_url": f"/download/{zip_path}"}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    return FileResponse(file_path, filename=filename, media_type="application/zip")
