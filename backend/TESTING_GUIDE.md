# 🧪 Backend Testing Guide - InvoiceIQ

## Complete Testing Strategy for Invoice Processing Pipeline

---

## 🎯 Testing Phases Completed

All 11 phases of backend development are now complete and ready for testing!

---

## 🚀 Quick Start Testing

### 1. Start the Server
```bash
cd backend
uvicorn main:app --reload
```

### 2. Open Swagger UI
Navigate to: **http://127.0.0.1:8000/docs**

---

## 📋 Test Endpoints

### 1. Health Check
```
GET http://127.0.0.1:8000/
GET http://127.0.0.1:8000/health
GET http://127.0.0.1:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "components": {
    "file_handler": "operational",
    "pdf_converter": "operational",
    "image_preprocessor": "operational",
    "ocr_engine": "operational",
    "regex_extractor": "operational",
    "table_extractor": "operational",
    "validator": "operational"
  }
}
```

### 2. Upload Single Invoice
```
POST http://127.0.0.1:8000/api/upload
Content-Type: multipart/form-data
Body: file=<invoice.jpg>
```

**Expected Response:**
```json
{
  "document_id": "DOC12AB34CD",
  "invoice_count": 1,
  "invoices": [{
    "invoice_number": "INV-001",
    "seller_name": "ABC Pvt Ltd",
    "buyer_name": "XYZ Ltd",
    "total_amount": 1200.00,
    ...
  }],
  "validation": {
    "is_valid": true,
    "validation_status": "valid",
    "errors": [],
    "warnings": []
  },
  "processing_time": 3.45
}
```

### 3. Upload Multiple Invoices
```
POST http://127.0.0.1:8000/api/upload/multiple
Content-Type: multipart/form-data
Body: files[]=<invoice1.jpg>, files[]=<invoice2.jpg>
```

---

## 🧪 Test Scenarios

### Scenario 1: Valid Image Invoice
**Test:** Upload clear JPG invoice  
**Expected:** Successful extraction with high confidence  
**Validation:** All fields extracted, calculations correct

### Scenario 2: PDF Invoice (Single Page)
**Test:** Upload single-page PDF  
**Expected:** PDF converted to image, then processed  
**Validation:** Same as image processing

### Scenario 3: PDF Invoice (Multi-Page)
**Test:** Upload multi-page PDF  
**Expected:** Each page processed separately  
**Validation:** Multiple invoices returned

### Scenario 4: Blurry/Low Quality Image
**Test:** Upload poor quality scan  
**Expected:** Preprocessing improves quality  
**Validation:** OCR still extracts text (may have lower confidence)

### Scenario 5: Invalid File Type
**Test:** Upload .txt or .doc file  
**Expected:** 400 error with clear message  
**Validation:** Error response format correct

### Scenario 6: File Too Large
**Test:** Upload file > 10MB  
**Expected:** 400 error  
**Validation:** Size limit enforced

### Scenario 7: Empty File
**Test:** Upload 0-byte file  
**Expected:** 400 error  
**Validation:** Empty file rejected

### Scenario 8: Invoice with Calculation Error
**Test:** Invoice where subtotal + tax ≠ total  
**Expected:** Validation error flagged  
**Validation:** Error message clear

### Scenario 9: Missing Required Fields
**Test:** Invoice without invoice number  
**Expected:** Validation warning  
**Validation:** Warning in response

### Scenario 10: Invoice with Line Items
**Test:** Invoice with itemized table  
**Expected:** Line items extracted  
**Validation:** Quantities, prices, totals correct

---

## 🔍 Component Testing

### Test 1: File Handler
```python
# Test file upload
# Test duplicate filename handling
# Test invalid file rejection
# Test file size validation
```

### Test 2: PDF Converter
```python
# Test single-page PDF
# Test multi-page PDF
# Test corrupted PDF
# Test non-PDF file
```

### Test 3: Image Preprocessor
```python
# Test grayscale conversion
# Test noise removal
# Test sharpening
# Test thresholding
# Test image quality improvement
```

### Test 4: OCR Engine
```python
# Test clear text extraction
# Test noisy image
# Test rotated image
# Test multi-language (if needed)
```

### Test 5: Regex Extractors
```python
# Test invoice number extraction
# Test date extraction
# Test GST number extraction
# Test amount extraction
# Test seller/buyer name extraction
```

### Test 6: Table Extractor
```python
# Test simple table
# Test complex table
# Test invoice without table
# Test malformed table
```

### Test 7: Validator
```python
# Test calculation validation
# Test required fields check
# Test GST format validation
# Test anomaly detection
```

---

## 📊 Performance Testing

### Metrics to Measure:
1. **Upload Time:** < 1 second
2. **PDF Conversion:** < 2 seconds per page
3. **Preprocessing:** < 1 second
4. **OCR Extraction:** < 3 seconds
5. **Field Extraction:** < 0.5 seconds
6. **Validation:** < 0.1 seconds
7. **Total Processing:** < 5 seconds per invoice

### Load Testing:
- Single file upload
- 10 files batch upload
- Concurrent requests (if applicable)

---

## 🐛 Error Testing

### Test Error Handling:
1. **Network Errors:** Simulate connection issues
2. **File System Errors:** Full disk, permission denied
3. **OCR Failures:** Tesseract not installed
4. **Memory Errors:** Very large files
5. **Timeout Errors:** Long processing times

### Expected Behavior:
- Graceful error messages
- No server crashes
- Proper HTTP status codes
- Detailed error logs

---

## 📝 Logging Verification

### Check Logs:
```bash
# View logs
cat backend/logs/invoice_processing_YYYYMMDD.log

# Check for:
- Upload events
- OCR start/complete
- Extraction events
- Validation results
- Error messages
- Processing times
```

---

## ✅ Acceptance Criteria

### Phase 1-11 Complete When:
- [ ] All endpoints respond correctly
- [ ] File upload works for JPG, PNG, PDF
- [ ] PDF conversion works
- [ ] Image preprocessing improves quality
- [ ] OCR extracts text accurately (>85%)
- [ ] Regex extracts all fields
- [ ] Table extraction works
- [ ] Validation catches errors
- [ ] JSON response format correct
- [ ] Logging captures all events
- [ ] Error handling is graceful

---

## 🔧 Testing Tools

### 1. Swagger UI (Recommended)
- Interactive API testing
- Built-in documentation
- Easy file upload
- Response visualization

### 2. Postman
- Collection management
- Environment variables
- Automated testing
- Response validation

### 3. cURL
```bash
# Health check
curl http://localhost:8000/health

# Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sample_invoice.jpg"
```

### 4. Python Script
```python
import requests

# Upload invoice
with open('invoice.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f}
    )
    print(response.json())
```

---

## 📦 Sample Test Data

### Create Sample Invoices:
```
backend/samples/
├── valid_invoice.jpg
├── blurry_invoice.jpg
├── multi_page.pdf
├── single_page.pdf
├── high_value_invoice.jpg
├── missing_gst.jpg
└── calculation_error.jpg
```

---

## 🎯 Test Results Template

```
Test Date: YYYY-MM-DD
Tester: [Name]

| Test Case | Status | Notes |
|-----------|--------|-------|
| Health Check | ✅ | All components operational |
| Upload JPG | ✅ | Processed in 3.2s |
| Upload PNG | ✅ | Processed in 2.8s |
| Upload PDF | ✅ | 2 pages, 5.1s total |
| Invalid File | ✅ | Proper error message |
| Large File | ✅ | Rejected correctly |
| Blurry Image | ⚠️ | Lower confidence (78%) |
| Calculation Error | ✅ | Validation caught error |
| Missing Fields | ✅ | Warnings generated |
| Line Items | ✅ | 5 items extracted |

Overall Status: PASS ✅
```

---

## 🚨 Known Limitations

1. **OCR Accuracy:** Depends on image quality
2. **Table Extraction:** Simple tables work best
3. **Regex Patterns:** May need tuning for different formats
4. **Language Support:** Currently English only
5. **Handwritten Text:** Not supported

---

## 🔄 Continuous Testing

### After Each Change:
1. Run health check
2. Test affected endpoint
3. Check logs for errors
4. Verify response format
5. Commit if tests pass

### Before Deployment:
1. Run full test suite
2. Test with real invoices
3. Performance testing
4. Error scenario testing
5. Integration testing with frontend

---

## 📞 Troubleshooting

### Issue: OCR Not Working
**Solution:** Check Tesseract installation
```bash
tesseract --version
```

### Issue: PDF Conversion Fails
**Solution:** Install poppler-utils

### Issue: Low OCR Accuracy
**Solution:** 
- Check image quality
- Adjust preprocessing parameters
- Try different PSM modes

### Issue: Validation Errors
**Solution:**
- Check calculation logic
- Verify tolerance settings
- Review validation rules

---

**Testing is critical! Test thoroughly before considering backend complete. 🧪**

