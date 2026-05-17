from typing import List, Optional
from pydantic import BaseModel, Field


class LineItemSchema(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    line_total: Optional[float] = None


class InvoiceSchema(BaseModel):
    invoice_id: str
    invoice_number: Optional[str] = None
    seller_name: Optional[str] = None
    buyer_name: Optional[str] = None
    issue_date: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    total_amount: Optional[float] = None
    payment_terms_days: Optional[int] = None
    page_start: int
    page_end: int
    line_items: List[LineItemSchema] = Field(default_factory=list)
    validation_errors: List[str] = Field(default_factory=list)
    confidence_score: float


class ExtractionResult(BaseModel):
    document_id: str
    file_path: str
    document_type: str
    invoice_count: int
    invoices: List[InvoiceSchema] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str
