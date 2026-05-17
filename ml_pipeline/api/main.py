"""
FastAPI application.

Endpoints:
  POST /extract   → upload a file, run pipeline, return structured JSON
  GET  /health    → liveness check
"""
import os
import uuid
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.schemas import ExtractionResult, ErrorResponse
from pipeline.logging_utils import configure_uvicorn, get_logger
from pipeline.pipeline import run as run_pipeline

# Route uvicorn's own loggers through our colored formatter so server startup
# lines look the same as pipeline lines.
configure_uvicorn()

log = get_logger("API")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

app = FastAPI(
    title="PS-2 Invoice Extractor",
    description="Detects and extracts structured data from invoice documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/extract",
    response_model=ExtractionResult,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def extract(file: UploadFile = File(...)):
    log.info(f"POST /extract received | filename={file.filename}")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        log.warning(f"Rejected upload — unsupported file type '{suffix}'")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Accepted: PDF, PNG, JPG.",
        )

    doc_id = str(uuid.uuid4())[:8]
    save_path = UPLOAD_DIR / f"{doc_id}{suffix}"

    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        log.debug(f"Saved upload to {save_path} | doc_id={doc_id}")
    except Exception as e:
        log.error(f"File save failed: {e}")
        raise HTTPException(status_code=500, detail=f"File save error: {e}")

    try:
        result = run_pipeline(str(save_path), document_id=doc_id)
    except Exception as e:
        log.critical(f"Pipeline failed for doc_id={doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")
    finally:
        save_path.unlink(missing_ok=True)

    log.info(
        f"Responding | doc_id={doc_id} | type={result.document_type} | "
        f"invoices={result.invoice_count}"
    )
    return ExtractionResult(**result.to_dict())


# Serve built React frontend (frontend/dist). In dev, the Vite dev server runs
# separately on port 5173 and proxies /extract + /health to this API.
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
