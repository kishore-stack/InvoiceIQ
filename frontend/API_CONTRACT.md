# API Contract - Frontend ↔️ Backend Integration

This document defines the exact API contract between the frontend (Member 1) and backend (Member 2).

---

## Base URL

```
Development: http://localhost:8000
Production: https://your-backend.onrender.com (Member 3 will configure)
```

---

## 1. Upload Invoice

### Endpoint
```
POST /upload
```

### Request
- **Content-Type:** `multipart/form-data`
- **Body:** 
  - `file` or `files`: File(s) to upload (image/*, application/pdf)

### Response (Success - 200)
```json
{
  "document_id": "DOC101",
  "invoice_count": 1,
  "invoices": [
    {
      "invoice_number": "INV-2024-001",
      "seller_name": "ABC Pvt Ltd",
      "seller_address": "123 Business St, City",
      "seller_gst": "29ABCDE1234F1Z5",
      "seller_contact": "+91-9876543210",
      "buyer_name": "XYZ Ltd",
      "buyer_address": "456 Commerce Ave, Town",
      "buyer_gst": "27XYZAB5678G2Y4",
      "buyer_contact": "+91-9123456780",
      "date": "2024-01-15",
      "total_amount": 1200.00,
      "subtotal": 1000.00,
      "tax_amount": 200.00,
      "discount": 0.00,
      "validation_status": "valid",
      "is_valid": true,
      "validation_errors": [],
      "validation_warnings": [],
      "confidence_score": 95.5,
      "line_items": [
        {
          "description": "Product A",
          "quantity": 2,
          "unit_price": 250.00,
          "price": 250.00,
          "tax": 50.00,
          "discount": 0.00,
          "total": 550.00
        },
        {
          "description": "Product B",
          "quantity": 1,
          "unit_price": 500.00,
          "price": 500.00,
          "tax": 100.00,
          "discount": 0.00,
          "total": 650.00
        }
      ]
    }
  ]
}
```

### Response (Error - 400)
```json
{
  "detail": "Invalid file format. Only JPG, PNG, and PDF are supported.",
  "error_type": "InvalidFileError"
}
```

### Response (Error - 500)
```json
{
  "detail": "OCR processing failed. Please ensure the image is clear and readable.",
  "error_type": "OCRError"
}
```

---

## 2. Get Invoice by ID

### Endpoint
```
GET /invoice/{document_id}
```

### URL Parameters
- `document_id` (string): The unique document identifier

### Response (Success - 200)
```json
{
  "document_id": "DOC101",
  "invoice_count": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "validation_status": "valid",
  "is_valid": true,
  "validation_errors": [],
  "validation_warnings": [],
  "confidence_score": 95.5,
  "invoices": [
    {
      "invoice_number": "INV-2024-001",
      "seller_name": "ABC Pvt Ltd",
      "buyer_name": "XYZ Ltd",
      "date": "2024-01-15",
      "total_amount": 1200.00,
      "subtotal": 1000.00,
      "tax_amount": 200.00,
      "discount": 0.00,
      "line_items": [...],
      "raw_text": "Full OCR extracted text..."
    }
  ]
}
```

### Response (Error - 404)
```json
{
  "detail": "Invoice not found",
  "error_type": "NotFoundError"
}
```

---

## 3. Get Invoice History

### Endpoint
```
GET /history
```

### Query Parameters (Optional)
- `skip` (int): Number of records to skip (pagination) - default: 0
- `limit` (int): Number of records to return - default: 100
- `status` (string): Filter by validation status ('valid', 'invalid', 'all') - default: 'all'

### Example Request
```
GET /history?skip=0&limit=20&status=valid
```

### Response (Success - 200)
```json
{
  "total": 50,
  "skip": 0,
  "limit": 20,
  "invoices": [
    {
      "document_id": "DOC101",
      "invoice_count": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "validation_status": "valid",
      "is_valid": true,
      "validation_errors": [],
      "confidence_score": 95.5,
      "invoices": [
        {
          "invoice_number": "INV-2024-001",
          "seller_name": "ABC Pvt Ltd",
          "buyer_name": "XYZ Ltd",
          "total_amount": 1200.00
        }
      ]
    },
    {
      "document_id": "DOC102",
      "invoice_count": 2,
      "created_at": "2024-01-14T09:15:00Z",
      "validation_status": "review",
      "is_valid": false,
      "validation_errors": ["Total amount mismatch"],
      "confidence_score": 78.2,
      "invoices": [...]
    }
  ]
}
```

**Alternative Format (Simple Array):**
The frontend also supports a simple array response:
```json
[
  {
    "document_id": "DOC101",
    "invoice_count": 1,
    "invoices": [...]
  },
  {
    "document_id": "DOC102",
    "invoice_count": 2,
    "invoices": [...]
  }
]
```

---

## 4. Delete Invoice

### Endpoint
```
DELETE /invoice/{document_id}
```

### URL Parameters
- `document_id` (string): The unique document identifier

### Response (Success - 200)
```json
{
  "message": "Invoice deleted successfully",
  "document_id": "DOC101"
}
```

### Response (Error - 404)
```json
{
  "detail": "Invoice not found",
  "error_type": "NotFoundError"
}
```

---

## Data Models

### Invoice Object (Complete)
```typescript
{
  // Identification
  invoice_number: string;
  
  // Seller Information
  seller_name: string;
  seller_address?: string;
  seller_gst?: string;
  seller_contact?: string;
  
  // Buyer Information
  buyer_name: string;
  buyer_address?: string;
  buyer_gst?: string;
  buyer_contact?: string;
  
  // Financial Information
  date?: string; // ISO date format
  subtotal?: number;
  tax_amount?: number;
  discount?: number;
  total_amount: number;
  
  // Line Items
  line_items?: LineItem[];
  
  // Metadata
  raw_text?: string; // Full OCR text
  confidence_score?: number; // 0-100
}
```

### Line Item Object
```typescript
{
  description: string; // or item_name
  quantity: number;
  unit_price: number; // or price
  tax?: number; // or tax_amount
  discount?: number;
  total?: number; // Calculated if not provided
  item_code?: string;
}
```

### Document Object
```typescript
{
  document_id: string;
  invoice_count: number;
  created_at?: string; // ISO datetime
  updated_at?: string; // ISO datetime
  
  // Validation
  validation_status: 'valid' | 'invalid' | 'review';
  is_valid: boolean;
  validation_errors: string[];
  validation_warnings?: string[];
  confidence_score: number; // 0-100
  
  // Invoices
  invoices: Invoice[];
}
```

---

## CORS Requirements

The backend **MUST** enable CORS for the frontend domain:

### Development
```python
# FastAPI example
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production
```python
allow_origins=[
    "http://localhost:5173",
    "https://your-frontend-domain.vercel.app"
]
```

---

## Error Response Format

All errors should follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_type": "ErrorCategory"
}
```

### Error Types

- `InvalidFileError` - File format not supported
- `OCRError` - OCR processing failed
- `ValidationError` - Data validation failed
- `NotFoundError` - Resource not found
- `ServerError` - Internal server error
- `NetworkError` - Network/connection issue

---

## File Upload Specifications

### Supported Formats
- JPG/JPEG
- PNG
- PDF

### Size Limits
- Maximum file size: 10MB per file
- Multiple files: Up to 10 files per request

### Form Data Structure

**Single File:**
```
POST /upload
Content-Type: multipart/form-data

file: <binary data>
```

**Multiple Files:**
```
POST /upload
Content-Type: multipart/form-data

files: <binary data>
files: <binary data>
files: <binary data>
```

---

## Testing Endpoints

### Using cURL

**Upload:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@invoice.pdf"
```

**Get Invoice:**
```bash
curl http://localhost:8000/invoice/DOC101
```

**Get History:**
```bash
curl http://localhost:8000/history
```

**Delete:**
```bash
curl -X DELETE http://localhost:8000/invoice/DOC101
```

### Using Python Requests

```python
import requests

# Upload
with open('invoice.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )

# Get invoice
response = requests.get('http://localhost:8000/invoice/DOC101')

# Get history
response = requests.get('http://localhost:8000/history')

# Delete
response = requests.delete('http://localhost:8000/invoice/DOC101')
```

---

## Frontend Usage

The frontend uses these endpoints via the `api.js` service:

```javascript
import api from './services/api';

// Upload
const result = await api.uploadInvoice(files, progressCallback);

// Get invoice
const invoice = await api.getInvoice(documentId);

// Get history
const history = await api.getHistory({ skip: 0, limit: 20 });

// Delete
await api.deleteInvoice(documentId);
```

---

## Notes for Backend Developer (Member 2)

1. **All endpoints must return JSON**
2. **Enable CORS for frontend domain**
3. **Use consistent error format**
4. **Include confidence scores in responses**
5. **Validation errors should be in array format**
6. **Line items calculations should be done by backend**
7. **Support both single and multiple file uploads**
8. **Return created_at/updated_at timestamps**
9. **Document IDs should be unique and persistent**
10. **Handle file size limits (reject > 10MB)**

---

## Validation Rules (Backend Responsibility)

The backend should validate:

1. **Total Amount:** `subtotal + tax - discount = total`
2. **Line Items:** Sum of all line item totals matches subtotal
3. **Required Fields:** invoice_number, seller_name, buyer_name, total_amount
4. **Date Format:** Valid date strings
5. **Numeric Values:** Positive numbers for amounts

---

## Timeline Expectations

1. **Member 2 implements endpoints:** 1-2 weeks
2. **Member 1 tests with backend:** 2-3 days
3. **Member 3 deploys both:** 1-2 days

---

**This contract ensures smooth integration between frontend and backend teams.**
