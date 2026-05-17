"""
Upload Route - Complete Invoice Processing Pipeline
Member 2: Backend Engineer
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import time
import uuid

# Import all processing modules
from utils.file_handler import file_handler
from utils.pdf_converter import pdf_converter
from preprocessing.image_cleaner import image_cleaner
from ocr.tesseract_engine import tesseract_ocr
from regex.invoice_regex import invoice_extractor
from regex.gst_regex import gst_extractor
from regex.amount_regex import amount_extractor
from extractor.table_extractor import table_extractor
from validator.invoice_validator import invoice_validator
from models.response_model import create_document_response, create_error_response
from utils.logger import logger

router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    """
    Complete invoice processing pipeline
    
    Pipeline:
    1. File validation and upload
    2. PDF to image conversion (if needed)
    3. Image preprocessing (OpenCV)
    4. OCR text extraction (Tesseract)
    5. Field extraction (Regex)
    6. Table extraction
    7. Validation
    8. JSON response formatting
    
    Args:
        file: Uploaded invoice file (image or PDF)
    
    Returns:
        Complete invoice data in standardized JSON format
    """
    start_time = time.time()
    document_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
    
    try:
        logger.log_api_request("/api/upload", "POST")
        
        # STEP 1: File Handling
        logger.info(f"Processing document: {document_id}")
        file_info = await file_handler.save_upload_file(file)
        
        if not file_info["success"]:
            logger.log_api_error("/api/upload", "File upload failed")
            return create_error_response("File upload failed", "FileUploadError")
        
        logger.log_upload(file_info["original_filename"], file_info["file_size_bytes"])
        file_path = file_info["file_path"]
        
        # STEP 2: PDF Conversion
        conversion_result = pdf_converter.convert_if_pdf(file_path)
        
        if not conversion_result["success"]:
            logger.error(f"PDF conversion failed: {conversion_result.get('error')}")
            return create_error_response(
                conversion_result.get("error", "PDF conversion failed"),
                "PDFConversionError"
            )
        
        image_paths = conversion_result["image_paths"]
        logger.info(f"Processing {len(image_paths)} image(s)")
        
        # Process each image (each page)
        invoices = []
        
        for idx, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {idx}/{len(image_paths)}: {image_path}")
            
            # STEP 3: Image Preprocessing
            preprocess_result = image_cleaner.preprocess_pipeline(image_path)
            
            if not preprocess_result["success"]:
                logger.warning(f"Preprocessing failed for {image_path}")
                continue
            
            processed_image = preprocess_result["processed_image"]
            
            # STEP 4: OCR Extraction
            logger.log_ocr_start(image_path)
            ocr_result = tesseract_ocr.extract_text_from_path(image_path)
            
            if not ocr_result["success"]:
                logger.log_ocr_failure(image_path, ocr_result.get("error", "Unknown"))
                continue
            
            ocr_text = ocr_result.get("text", "")
            if not ocr_text or not isinstance(ocr_text, str):
                ocr_text = str(ocr_text) if ocr_text else ""
                
            logger.log_ocr_complete(image_path, ocr_result.get("char_count", 0))
            
            # STEP 5: Field Extraction
            logger.log_extraction_start(document_id)
            
            # Extract invoice fields
            invoice_fields = invoice_extractor.extract_all_fields(ocr_text)
            
            # Extract GST information
            gst_numbers = gst_extractor.extract_all_gst_numbers(ocr_text)
            tax_info = gst_extractor.extract_cgst_sgst(ocr_text)
            
            # Extract amounts
            amounts = amount_extractor.extract_all_amounts(ocr_text)
            
            # STEP 6: Table Extraction
            table_result = table_extractor.extract_table_data(ocr_text)
            line_items = table_result["line_items"]
            
            # Combine all extracted data
            invoice_data = {
                "invoice_number": invoice_fields.get("invoice_number") or "UNKNOWN",
                "date": invoice_fields.get("date"),
                "seller_name": invoice_fields.get("seller_name") or "Unknown Seller",
                "seller_gst": gst_numbers[0] if len(gst_numbers) > 0 else None,
                "buyer_name": invoice_fields.get("buyer_name") or "Unknown Buyer",
                "buyer_gst": gst_numbers[1] if len(gst_numbers) > 1 else None,
                "subtotal": amounts.get("subtotal"),
                "tax_amount": tax_info.get("total_tax"),
                "cgst": tax_info.get("cgst"),
                "sgst": tax_info.get("sgst"),
                "igst": tax_info.get("igst"),
                "discount": amounts.get("discount", 0.0),
                "total_amount": amounts.get("total_amount"),
                "line_items": line_items,
                "raw_text": ocr_text,
                "confidence_score": 85.0  # Placeholder
            }
            
            logger.log_extraction_complete(document_id, len([v for v in invoice_data.values() if v]))
            
            # STEP 7: Validation
            validation_result = invoice_validator.validate_invoice(invoice_data)
            logger.log_validation_result(
                document_id,
                validation_result["is_valid"],
                len(validation_result["errors"])
            )
            
            invoices.append(invoice_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.log_processing_time(document_id, processing_time)
        
        # STEP 8: Create standardized response
        if not invoices:
            return create_error_response(
                "No invoices could be processed from the uploaded file",
                "ProcessingError"
            )
        
        # Get validation for first invoice (or aggregate)
        validation = invoice_validator.validate_invoice(invoices[0]) if invoices else None
        
        response = create_document_response(
            document_id=document_id,
            invoices=invoices,
            validation=validation,
            processing_time=processing_time
        )
        
        logger.info(f"Successfully processed document: {document_id}")
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.log_api_error("/api/upload", str(e))
        return create_error_response(
            f"Processing failed: {str(e)}",
            "InternalError"
        )



@router.get("/health")
async def health_check():
    """
    Check health of all processing components
    
    Returns:
        Status of each component
    """
    # Test Tesseract availability
    ocr_status = tesseract_ocr.test_ocr_availability()
    
    return {
        "status": "healthy",
        "components": {
            "file_handler": "operational",
            "pdf_converter": "operational",
            "image_preprocessor": "operational",
            "ocr_engine": "operational" if ocr_status["available"] else "unavailable",
            "regex_extractor": "operational",
            "table_extractor": "operational",
            "validator": "operational"
        },
        "ocr_info": ocr_status
    }


@router.post("/upload/multiple")
async def upload_multiple_invoices(files: List[UploadFile] = File(...)):
    """
    Upload multiple invoice files
    
    Args:
        files: List of uploaded invoice files
    
    Returns:
        Batch processing results
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per upload"
        )
    
    results = []
    
    for file in files:
        try:
            # Process each file using the main upload endpoint logic
            result = await upload_invoice(file)
            results.append({
                "filename": file.filename,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "status": "batch processing complete",
        "total_files": len(files),
        "results": results
    }

