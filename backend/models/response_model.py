"""
Response Model - Standardized JSON Schema for Invoice Data
Member 2: Backend Engineer

Ensures consistent API responses for frontend integration
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class LineItem(BaseModel):
    """
    Individual line item in an invoice
    """
    item: str = Field(..., description="Item description")
    quantity: float = Field(default=1.0, description="Item quantity")
    price: Optional[float] = Field(None, description="Item price")
    tax: Optional[float] = Field(0.0, description="Tax amount")
    discount: Optional[float] = Field(0.0, description="Discount amount")
    line_total: Optional[float] = Field(None, description="Line item total")

class Invoice(BaseModel):
    """
    Single invoice data structure
    """
    # Identification
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    date: Optional[str] = Field(None, description="Invoice date")
    
    # Seller information
    seller_name: Optional[str] = Field(None, description="Seller/vendor name")
    seller_address: Optional[str] = Field(None, description="Seller address")
    seller_gst: Optional[str] = Field(None, description="Seller GST number")
    seller_contact: Optional[str] = Field(None, description="Seller contact")
    
    # Buyer information
    buyer_name: Optional[str] = Field(None, description="Buyer/customer name")
    buyer_address: Optional[str] = Field(None, description="Buyer address")
    buyer_gst: Optional[str] = Field(None, description="Buyer GST number")
    buyer_contact: Optional[str] = Field(None, description="Buyer contact")
    
    # Financial information
    subtotal: Optional[float] = Field(None, description="Subtotal amount")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    cgst: Optional[float] = Field(None, description="CGST amount")
    sgst: Optional[float] = Field(None, description="SGST amount")
    igst: Optional[float] = Field(None, description="IGST amount")
    discount: Optional[float] = Field(0.0, description="Discount amount")
    total_amount: Optional[float] = Field(None, description="Total amount")
    
    # Line items
    line_items: List[LineItem] = Field(default_factory=list, description="Invoice line items")
    
    # Metadata
    raw_text: Optional[str] = Field(None, description="Raw OCR text")
    confidence_score: Optional[float] = Field(None, description="OCR confidence (0-100)")
    
    # Validation
    validation: Optional['ValidationResult'] = Field(None, description="Validation results")

class ValidationResult(BaseModel):
    """
    Validation result structure
    """
    validation_status: bool = Field(..., description="Overall validation status")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")

class DocumentResponse(BaseModel):
    """
    Complete document response - Main API response format
    """
    document_id: str = Field(..., description="Unique document identifier")
    invoice_count: int = Field(..., description="Number of invoices in document")
    invoices: List[Invoice] = Field(..., description="List of invoices")
    
    # Processing metadata
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Processing timestamp")

class ErrorResponse(BaseModel):
    """
    Error response format
    """
    status: str = Field("error", description="Status string")
    message: str = Field(..., description="Clean error message")
    document_id: str = Field("", description="Document ID if available")
    invoice_count: int = Field(0, description="Always 0 for errors")
    invoices: list = Field(default_factory=list, description="Always empty for errors")

class UploadResponse(BaseModel):
    """
    Upload endpoint response
    """
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Response message")
    document_id: Optional[str] = Field(None, description="Generated document ID")
    file_info: Optional[dict] = Field(None, description="Uploaded file information")


def create_document_response(
    document_id: str,
    invoices: List[dict],
    validation: Optional[dict] = None,
    processing_time: Optional[float] = None
) -> dict:
    """
    Helper function to create standardized document response
    
    Args:
        document_id: Unique document identifier
        invoices: List of invoice dictionaries
        processing_time: Processing time in seconds
        
    Returns:
        Standardized response dictionary
    """
    return {
        "document_id": document_id,
        "invoice_count": len(invoices),
        "invoices": invoices,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }


def create_error_response(error_message: str, document_id: str = "") -> dict:
    """
    Helper function to create standardized error response with stable schema
    
    Args:
        error_message: Clean error message to show user
        document_id: Optional document ID if failed midway
        
    Returns:
        Standardized error response matching frontend expectations
    """
    return {
        "status": "error",
        "message": error_message,
        "document_id": document_id,
        "invoice_count": 0,
        "invoices": []
    }
