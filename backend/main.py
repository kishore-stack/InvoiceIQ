from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Database imports
from database.db import engine, Base, get_db
from models.db_models import DBInvoice
import models.db_models

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="InvoiceIQ Backend API",
    description="AI-powered invoice processing system",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROOT
# =========================================
@app.get("/")
async def root():
    return {
        "status": "Backend Running",
        "service": "InvoiceIQ Backend API",
        "version": "1.0.0"
    }

# =========================================
# HEALTH CHECK
# =========================================
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

# =========================================
# HISTORY API
# =========================================
@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):

    invoices = db.query(DBInvoice).order_by(DBInvoice.created_at.desc()).all()

    result = []

    for inv in invoices:
        result.append({
            "id": inv.id,
            "document_id": inv.document_id,
            "invoice_number": inv.invoice_number,
            "date": inv.date,
            "seller_name": inv.seller_name,
            "buyer_name": inv.buyer_name,
            "seller_gst": inv.seller_gst,
            "buyer_gst": inv.buyer_gst,
            "subtotal": inv.subtotal,
            "tax_amount": inv.tax_amount,
            "total_amount": inv.total_amount,
            "validation_status": inv.validation_status,
            "processing_time": inv.processing_time,
            "created_at": str(inv.created_at)
        })

    return {
        "status": "success",
        "count": len(result),
        "data": result
    }

# =========================================
# IMPORT ROUTES
# =========================================
from routes import upload, test_upload, test_ocr

# =========================================
# INCLUDE ROUTERS
# =========================================
app.include_router(upload.router)
app.include_router(test_upload.router)
app.include_router(test_ocr.router)

# =========================================
# RUN SERVER
# =========================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

   