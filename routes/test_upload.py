"""
Test Upload Route - Simple file handling and PDF conversion test
Member 2: Backend Engineer

This endpoint tests ONLY file handling and PDF conversion
WITHOUT OCR processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_handler import file_handler
from utils.pdf_converter import pdf_converter

router = APIRouter(prefix="/api/test", tags=["Testing"])

@router.post("/upload-simple")
async def test_upload_simple(file: UploadFile = File(...)):
    """
    Simple upload test - File handling and PDF conversion only
    
    Tests:
    1. File upload and storage
    2. PDF to image conversion (if PDF)
    3. Returns file paths
    
    Does NOT include:
    - OCR processing
    - Field extraction
    - Validation
    
    Args:
        file: Uploaded invoice file (JPG, PNG, or PDF)
    
    Returns:
        File processing results
    """
    try:
        # STEP 1: Save uploaded file
        file_info = await file_handler.save_upload_file(file)
        
        if not file_info["success"]:
            raise HTTPException(
                status_code=400,
                detail="File upload failed"
            )
        
        file_path = file_info["file_path"]
        
        # STEP 2: Convert PDF to images (if needed)
        conversion_result = pdf_converter.convert_if_pdf(file_path)
        
        if not conversion_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"PDF conversion failed: {conversion_result.get('error')}"
            )
        
        # STEP 3: Return results
        return {
            "status": "file processed successfully",
            "file_info": {
                "original_filename": file_info["original_filename"],
                "saved_filename": file_info["saved_filename"],
                "file_size_mb": file_info["file_size_mb"],
                "file_type": file_info["file_type"]
            },
            "conversion": {
                "is_pdf": conversion_result["is_pdf"],
                "page_count": conversion_result["page_count"],
                "image_paths": conversion_result["image_paths"]
            },
            "message": "File uploaded and processed. Ready for OCR (not implemented in this test endpoint)."
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("/health")
async def test_health():
    """
    Test health check for file handling components
    """
    import os
    
    # Check if directories exist
    uploads_exist = os.path.exists("backend/uploads")
    outputs_exist = os.path.exists("backend/outputs")
    
    return {
        "status": "healthy",
        "components": {
            "file_handler": "operational",
            "pdf_converter": "operational",
            "uploads_directory": "exists" if uploads_exist else "missing",
            "outputs_directory": "exists" if outputs_exist else "missing"
        },
        "message": "File handling and PDF conversion ready for testing"
    }
