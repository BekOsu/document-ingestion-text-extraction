import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import RAW_DIR, PROCESSED_DIR
from app.ingestion.downloader import download_pdf
from app.extraction.extractor import extract_text, get_supported_extensions
from app.export.exporter import export_to_json, export_to_csv

app = FastAPI(title="Document Extraction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    url: str


class ExtractionResult(BaseModel):
    file_name: str
    page_count: int | None
    extraction_method: str | None
    extracted_text: str | None
    success: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/supported-formats")
def supported_formats():
    return {"extensions": get_supported_extensions()}


@app.post("/extract/file", response_model=ExtractionResult)
async def extract_from_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    supported = get_supported_extensions()

    if suffix not in supported:
        raise HTTPException(400, f"Unsupported format. Supported: {supported}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        result = extract_text(tmp_path)
        return ExtractionResult(**result)
    finally:
        tmp_path.unlink(missing_ok=True)


@app.post("/extract/url", response_model=ExtractionResult)
async def extract_from_url(request: URLRequest):
    file_path = download_pdf(request.url)
    if not file_path:
        raise HTTPException(400, "Failed to download file")

    result = extract_text(file_path)
    result["source_url"] = request.url
    return ExtractionResult(**result)


@app.post("/extract/batch")
async def extract_batch(files: list[UploadFile] = File(...)):
    results = []
    supported = get_supported_extensions()

    for file in files:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in supported:
            results.append({
                "file_name": file.filename,
                "success": False,
                "error": "Unsupported format",
            })
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        try:
            result = extract_text(tmp_path)
            results.append(result)
        finally:
            tmp_path.unlink(missing_ok=True)

    return {"results": results, "total": len(results)}


@app.post("/export/json")
async def export_json(files: list[UploadFile] = File(...)):
    batch_result = await extract_batch(files)
    records = batch_result["results"]
    output_path = export_to_json(records)
    return FileResponse(output_path, filename=output_path.name, media_type="application/json")


@app.post("/export/csv")
async def export_csv(files: list[UploadFile] = File(...)):
    batch_result = await extract_batch(files)
    records = batch_result["results"]
    output_path = export_to_csv(records)
    return FileResponse(output_path, filename=output_path.name, media_type="text/csv")