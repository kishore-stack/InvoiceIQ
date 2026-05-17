"""
Test OCR Route - Test preprocessing and OCR pipeline
Member 2: Backend Engineer

Tests ONLY: File Upload → PDF Conversion → Preprocessing → OCR
Does NOT test: Regex extraction, validation, etc.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_handler import file_handler
from utils.pdf_converter import pdf_converter
from preprocessing.image_cleaner import image_cleaner
from ocr.tesseract_engine import tesseract_ocr

router = APIRouter(prefix="/api/test", tags=["OCR Testing"])

@router.post("/ocr-pipeline")
async def test_ocr_pipeline(file: UploadFile = File(...)):
    """
    Test complete OCR pipeline
    
    Pipeline:
    1. Upload file
    2. Convert PDF (if needed)
    3. Preprocess images
    4. Extract OCR text
    5. Return results
    
    Does NOT include:
    - Field extraction (regex)
    - Table extraction
    - Validation
    
    Args:
        file: Invoice file (JPG, PNG, or PDF)
    
    Returns:
        OCR extraction results
    """
    try:
        # STEP 1: Save uploaded file
        file_info = await file_handler.save_upload_file(file)
        
        if not file_info["success"]:
            raise HTTPException(status_code=400, detail="File upload failed")
        
        file_path = file_info["file_path"]
        
        # STEP 2: Convert PDF to images (if needed)
        conversion_result = pdf_converter.convert_if_pdf(file_path)
        
        if not conversion_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"PDF conversion failed: {conversion_result.get('error')}"
            )
        
        image_paths = conversion_result["image_paths"]
        
        # STEP 3 & 4: Process each image
        ocr_results = []
        
        for idx, image_path in enumerate(image_paths, 1):
            # Preprocess image
            preprocess_result = image_cleaner.preprocess_pipeline(image_path, save_output=True)
            
            if not preprocess_result["success"]:
                ocr_results.append({
                    "page": idx,
                    "status": "preprocessing_failed",
                    "error": preprocess_result.get("error"),
                    "text": ""
                })
                continue
            
            # Extract OCR text
            processed_path = preprocess_result["processed_path"]
            ocr_result = tesseract_ocr.extract_and_save(processed_path, save_log=True)
            
            if not ocr_result["success"]:
                ocr_results.append({
                    "page": idx,
                    "status": "ocr_failed",
                    "error": ocr_result.get("error"),
                    "text": ""
                })
                continue
            
            # Success
            ocr_results.append({
                "page": idx,
                "status": "success",
                "text": ocr_result["text"],
                "char_count": ocr_result.get("char_count", 0),
                "line_count": ocr_result.get("line_count", 0),
                "processed_image": processed_path,
                "ocr_log": ocr_result.get("log_path")
            })
        
        # STEP 5: Return results
        return {
            "status": "ocr pipeline completed",
            "file_info": {
                "original_filename": file_info["original_filename"],
                "file_type": file_info["file_type"]
            },
            "conversion": {
                "is_pdf": conversion_result["is_pdf"],
                "page_count": conversion_result["page_count"]
            },
            "ocr_results": ocr_results,
            "message": "OCR extraction complete. Check outputs/ for processed images and logs."
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR pipeline failed: {str(e)}"
        )


@router.get("/ocr-health")
async def test_ocr_health():
    """
    Check OCR pipeline health
    """
    # Test Tesseract availability
    ocr_status = tesseract_ocr.test_ocr_availability()
    
    import os
    outputs_exist = os.path.exists("backend/outputs")
    
    return {
        "status": "healthy" if ocr_status["available"] else "degraded",
        "components": {
            "file_handler": "operational",
            "pdf_converter": "operational",
            "image_preprocessor": "operational",
            "tesseract_ocr": "operational" if ocr_status["available"] else "unavailable"
        },
        "tesseract": ocr_status,
        "outputs_directory": "exists" if outputs_exist else "missing",
        "message": "OCR pipeline ready" if ocr_status["available"] else "Tesseract not found"
    }


@router.post("/test-preprocessing")
async def test_preprocessing_only(file: UploadFile = File(...)):
    """
    Test ONLY image preprocessing (no OCR)
    
    Useful for debugging preprocessing quality
    """
    try:
        # Save file
        file_info = await file_handler.save_upload_file(file)
        if not file_info["success"]:
            raise HTTPException(status_code=400, detail="File upload failed")
        
        file_path = file_info["file_path"]
        
        # Convert PDF if needed
        conversion_result = pdf_converter.convert_if_pdf(file_path)
        if not conversion_result["success"]:
            raise HTTPException(status_code=500, detail="PDF conversion failed")
        
        image_paths = conversion_result["image_paths"]
        
        # Preprocess each image
        preprocessing_results = []
        
        for idx, image_path in enumerate(image_paths, 1):
            result = image_cleaner.preprocess_pipeline(image_path, save_output=True)
            
            preprocessing_results.append({
                "page": idx,
                "success": result["success"],
                "original_path": image_path,
                "processed_path": result.get("processed_path"),
                "error": result.get("error")
            })
        
        return {
            "status": "preprocessing completed",
            "page_count": len(image_paths),
            "results": preprocessing_results,
            "message": "Check backend/outputs/ for processed images"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
