"""
Upload Route - File Upload Handler
Member 2: Backend Engineer
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    """
    Upload invoice file for processing
    
    Currently: Basic file upload validation
    Future: OCR processing, extraction, validation
    
    Args:
        file: Uploaded invoice file (image or PDF)
    
    Returns:
        Success response with file details
    """
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: JPG, PNG, PDF"
        )
    
    # Get file size
    content = await file.read()
    file_size = len(content)
    
    # Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 10MB"
        )
    
    # Reset file pointer for future processing
    await file.seek(0)
    
    return {
        "status": "uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file_size,
        "size_mb": round(file_size / (1024 * 1024), 2),
        "message": "File received. OCR processing will be implemented next.",
        "next_steps": [
            "Image preprocessing (OpenCV)",
            "OCR extraction (Tesseract)",
            "Regex field extraction",
            "Table extraction",
            "Validation"
        ]
    }

@router.post("/upload/multiple")
async def upload_multiple_invoices(files: List[UploadFile] = File(...)):
    """
    Upload multiple invoice files
    
    Args:
        files: List of uploaded invoice files
    
    Returns:
        Success response with all file details
    """
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per upload"
        )
    
    results = []
    
    for file in files:
        # Validate each file
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        
        if file.content_type not in allowed_types:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": "Invalid file type"
            })
            continue
        
        content = await file.read()
        file_size = len(content)
        
        results.append({
            "filename": file.filename,
            "status": "uploaded successfully",
            "size_mb": round(file_size / (1024 * 1024), 2)
        })
    
    return {
        "status": "batch upload complete",
        "total_files": len(files),
        "results": results
    }
