"""
InvoiceIQ Backend - Main FastAPI Application
Member 2: Backend Engineer
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="InvoiceIQ Backend API",
    description="AI-powered invoice processing system - Backend processing engine",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    """
    Health check endpoint
    Returns backend status
    """
    return {
        "status": "Backend Running",
        "service": "InvoiceIQ Backend API",
        "version": "1.0.0",
        "message": "Backend processing engine is operational"
    }

@app.get("/health")
async def health_check():
    """
    Detailed health check
    """
    return {
        "status": "healthy",
        "service": "InvoiceIQ Backend",
        "components": {
            "api": "operational",
            "ocr": "pending_implementation",
            "preprocessing": "pending_implementation",
            "extraction": "pending_implementation",
            "validation": "pending_implementation"
        }
    }

# Import routes
from routes import upload, test_upload

# Include routers
app.include_router(upload.router)
app.include_router(test_upload.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
