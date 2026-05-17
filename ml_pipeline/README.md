# Multi-Invoice Detection Dataset

A comprehensive machine learning pipeline for detecting, segmenting, and extracting structured data from multi-invoice documents (PDFs and images). This project includes synthetic dataset generation, OCR processing, invoice classification, and a FastAPI-based extraction service.

## Project Overview

This repository provides an end-to-end solution for invoice document processing:

- **Dataset Generation**: Create synthetic multi-invoice documents with realistic variations and noise
- **Document Processing Pipeline**: Preprocess, classify, segment, and extract invoice data
- **OCR Integration**: Extract text from documents using Tesseract
- **Field Extraction**: Intelligently parse invoice fields (dates, amounts, seller/buyer info)
- **Table Extraction**: Extract line items from invoice tables
- **API Service**: REST API for document processing and data extraction
- **Evaluation Framework**: Validate extraction accuracy against ground truth

## Repository Structure

```
├── api/                          # FastAPI application
│   ├── main.py                  # API endpoints and server setup
│   ├── schemas.py               # Pydantic data models for API responses
│   └── __init__.py
│
├── pipeline/                     # Core extraction pipeline
│   ├── pipeline.py              # Main orchestration (coordinates all stages)
│   ├── preprocessor.py          # Image preprocessing (resize, denoise, binarization)
│   ├── page_classifier.py       # Classify pages as invoice or non-invoice
│   ├── invoice_segmenter.py     # Segment multiple invoices in a document
│   ├── ocr.py                   # Tesseract OCR integration
│   ├── field_extractor.py       # Extract key fields (dates, amounts, names)
│   ├── table_extractor.py       # Extract line items and tables
│   ├── validator.py             # Validate extracted data and compute confidence
│   ├── logging_utils.py         # Colored logging configuration
│   └── __init__.py
│
├── generator/                    # Synthetic dataset generation
│   ├── generate.py              # Main generation script
│   ├── faker_data.py            # Generate realistic invoice data using Faker
│   ├── templates.py             # Invoice layout templates
│   ├── augment.py               # Image augmentation (noise, rotation, blur)
│   └── __init__.py
│
├── documents/                    # Generated synthetic documents (PDFs/images)
│
├── annotations.json             # Ground truth invoice data and metadata
├── train_manifest.csv           # Training dataset manifest (file paths and splits)
├── test_manifest.csv            # Test dataset manifest
├── evaluate.py                  # Evaluation script for pipeline accuracy
└── requirements.txt             # Python dependencies
```

## Key Features

### 1. **Synthetic Dataset Generation**
- Creates realistic multi-invoice documents with 500+ examples by default
- Supports configurable document complexity (single/multiple invoices per page)
- Realistic data generation using Faker library
- Image augmentation with noise, rotation, blur, and perspective distortion
- PDF and image export formats

### 2. **Document Processing Pipeline**
- **Preprocessing**: Image enhancement, resizing, denoising, binarization
- **Page Classification**: Distinguishes invoice pages from non-invoice content
- **Invoice Segmentation**: Detects and segments multiple invoices within a single document
- **OCR Processing**: Extracts text using Tesseract with language support
- **Field Extraction**: Parses structured fields:
  - Invoice metadata (number, date, currency)
  - Seller and buyer information
  - Financial data (subtotal, tax, discount, total)
  - Payment terms
- **Table Extraction**: Extracts line items with description, quantity, unit price, tax, discount
- **Validation**: Validates extracted data and computes confidence scores

### 3. **REST API**
- **POST /extract**: Upload a document (PDF/PNG/JPG) and extract invoice data
- **GET /health**: Health check endpoint
- CORS enabled for cross-origin requests
- Structured JSON responses with full invoice details

### 4. **Evaluation Framework**
- Compares pipeline output against ground truth annotations
- Computes accuracy metrics for:
  - String fields (invoice number, seller, buyer names)
  - Numeric fields (amounts, quantities) with configurable tolerance
  - Line item counts
  - Individual line item matching
- Generates detailed reports

## Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR engine (required for text extraction)

### Install Tesseract
- **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

### Setup Python Environment

```bash
# Clone or navigate to the repository
cd multi-invoice-detection-dataset

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Generate Synthetic Dataset

Create 500 synthetic invoice documents with annotations:

```bash
python -m generator.generate --output-dir . --count 500
```

This generates:
- `documents/`: PDF and PNG files
- `annotations.json`: Ground truth data for all documents
- `train_manifest.csv`: Training set manifest (80%)
- `test_manifest.csv`: Test set manifest (20%)

**Options:**
- `--output-dir`: Output directory (default: current directory)
- `--count`: Number of documents to generate (default: 500)

### 2. Run the Extraction Pipeline

Extract invoice data from a single document:

```bash
python -c "
from pipeline.pipeline import run as run_pipeline
result = run_pipeline('documents/doc_0001.pdf')
print(result)
"
```

Or programmatically:

```python
from pipeline.pipeline import run as run_pipeline

# Process a document
result = run_pipeline('path/to/document.pdf')

# Access extracted data
for invoice in result.invoices:
    print(f"Invoice: {invoice.invoice_number}")
    print(f"Total: {invoice.total_amount}")
    for item in invoice.line_items:
        print(f"  - {item.description}: {item.line_total}")
```

### 3. Evaluate Pipeline Accuracy

Run the pipeline on test documents and compute accuracy metrics:

```bash
python evaluate.py --manifest test_manifest.csv --annotations annotations.json
```

This produces:
- Per-field accuracy metrics
- Per-document accuracy
- Overall pipeline performance report
- Error analysis and confidence statistics

### 4. Start API Server

Launch the FastAPI extraction service:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**API Usage:**

Upload and extract invoice data:

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@documents/doc_0001.pdf"
```

**Response:**

```json
{
  "status": "success",
  "document_id": "doc_0001",
  "invoice_count": 2,
  "invoices": [
    {
      "invoice_id": "doc_0001_inv_1",
      "invoice_number": "INV-2013-7622",
      "seller_name": "Johnson LLC",
      "buyer_name": "Stevens, Martinez and Nielsen",
      "issue_date": "2026-02-28",
      "currency": "GBP",
      "subtotal": 1808218.52,
      "tax_amount": 44663.0,
      "discount_amount": 136882.14,
      "total_amount": 1831637.56,
      "payment_terms_days": 7,
      "line_items": [
        {
          "description": "Web Development Services",
          "quantity": 5.56,
          "unit_price": 1115.77,
          "tax_amount": 620.37,
          "discount_amount": 310.18,
          "line_total": 6513.87
        }
      ],
      "confidence": 0.95
    }
  ]
}
```

## Dependencies

Core libraries:

- **FastAPI** / **Uvicorn**: Web framework and ASGI server
- **PyMuPDF** (fitz): PDF processing and rendering
- **pdfplumber**: PDF table extraction
- **Tesseract** / **pytesseract**: OCR for text extraction
- **OpenCV** (opencv-python-headless): Image processing
- **Pillow**: Image manipulation
- **ReportLab**: PDF generation for synthetic documents
- **Faker**: Realistic data generation
- **Pydantic**: Data validation
- **pandas**: Data manipulation and CSV handling
- **scikit-learn**: Machine learning utilities
- **dateparser**: Date parsing and normalization
- **NumPy**: Numerical operations

See [requirements.txt](requirements.txt) for specific versions.

## Data Format

### Annotations Format (annotations.json)

Ground truth data for evaluation:

```json
{
  "document_id": "doc_0001",
  "document_type": "repeated_invoice_copy",
  "invoice_count": 2,
  "file_path": "documents/doc_0001.pdf",
  "noise_level": "medium",
  "invoices": [
    {
      "invoice_id": "doc_0001_inv_1",
      "invoice_number": "INV-2013-7622",
      "seller_name": "Johnson LLC",
      "buyer_name": "Stevens, Martinez and Nielsen",
      "issue_date": "2026-02-28",
      "currency": "GBP",
      "subtotal": 1808218.52,
      "tax_amount": 44663.0,
      "discount_amount": 136882.14,
      "total_amount": 1831637.56,
      "payment_terms_days": 7,
      "page_start": 1,
      "page_end": 1,
      "line_items": [...]
    }
  ]
}
```

### Manifest Format (train_manifest.csv, test_manifest.csv)

CSV files mapping documents to their annotations:

```
document_id,file_path,split
doc_0001,documents/doc_0001.pdf,train
doc_0002,documents/doc_0002.pdf,test
...
```

## Pipeline Architecture

The extraction pipeline follows this flow:

```
1. Input Document (PDF/Image)
         ↓
2. Preprocessing (denoise, binarize, optimize)
         ↓
3. Page Classification (invoice vs non-invoice)
         ↓
4. Invoice Segmentation (detect invoice boundaries)
         ↓
5. OCR (extract text from regions)
         ↓
6. Field Extraction (parse structured fields)
         ↓
7. Table Extraction (extract line items)
         ↓
8. Validation (validate data, compute confidence)
         ↓
Output: Structured Invoice Data (JSON)
```

## Configuration & Customization

### Customize Invoice Templates
Edit [generator/templates.py](generator/templates.py) to add new invoice layout templates.

### Adjust OCR Settings
Modify [pipeline/ocr.py](pipeline/ocr.py) for language support or OCR engine configuration.

### Field Extraction Rules
Update [pipeline/field_extractor.py](pipeline/field_extractor.py) to add or modify field extraction logic.

### Evaluation Metrics
Adjust tolerance thresholds in [evaluate.py](evaluate.py) for numeric field matching.

## Troubleshooting

### Tesseract Not Found
Ensure Tesseract is installed and the path is correctly set in your system PATH, or configure the path explicitly:

```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### PDF Processing Issues
Verify PDF is not corrupted and supports text extraction. Some scanned PDFs may require preprocessing.

### Low OCR Accuracy
- Ensure image quality is sufficient (DPI ≥ 150)
- Check that preprocessing parameters are optimized for document type
- Consider training custom Tesseract models for specialized documents

## Performance Notes

- **Dataset Generation**: ~50-100 documents per minute (depending on invoice complexity)
- **Pipeline Processing**: ~5-15 seconds per document (PDF parsing, OCR, extraction)
- **API Throughput**: ~4-8 documents per second with uvicorn workers

Optimize with:
- GPU-accelerated OCR libraries for high-throughput scenarios
- Parallel processing for batch operations
- Caching for repeated documents

## License & Attribution

This project is provided as-is for educational and development purposes.

## Contributing

Contributions welcome! Areas for enhancement:
- Multi-language OCR support
- Advanced table detection and extraction
- Machine learning-based field classification
- Performance optimization
- Additional invoice templates

## Support

For issues, questions, or suggestions, refer to the code documentation in each module.
