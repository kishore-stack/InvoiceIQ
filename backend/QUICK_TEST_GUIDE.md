# 🚀 Quick Test Guide - InvoiceIQ Backend

## Fast Testing Reference

---

## 📋 Prerequisites

✅ Python 3.11+ installed  
✅ Virtual environment activated  
✅ Dependencies installed  
✅ Tesseract OCR installed  

---

## 🎯 Quick Start (3 Steps)

### 1. Start Server
```bash
cd backend
python start_server.py
```

### 2. Open Swagger UI
```
http://localhost:8000/docs
```

### 3. Test Endpoints
Use Swagger UI to test each endpoint interactively

---

## 🧪 Test Commands

### Phase 1: File Handling
```bash
python test_file_handling.py
python test_file_handling.py samples/invoice.jpg
```

### Phase 2: OCR Pipeline
```bash
python test_ocr_pipeline.py
python test_ocr_pipeline.py samples/invoice.jpg
```

### Full Pipeline (All Phases)
```bash
python test_pipeline.py samples/invoice.jpg
```

---

## 📍 Available Test Endpoints

### File Handling Tests
- `POST /api/test/upload-simple` - Test file upload
- `GET /api/test/health` - File handler health

### OCR Tests
- `POST /api/test/ocr-pipeline` - Full OCR test
- `POST /api/test/test-preprocessing` - Preprocessing only
- `GET /api/test/ocr-health` - OCR health check

### Full Pipeline
- `POST /api/upload` - Complete processing
- `POST /api/upload/multiple` - Batch processing
- `GET /api/health` - Full system health

---

## 📂 Check Outputs

### Uploaded Files
```bash
ls backend/uploads/
```

### Processed Images
```bash
ls backend/outputs/*_processed.png
```

### OCR Logs
```bash
cat backend/outputs/*_ocr.txt
```

### PDF Converted Pages
```bash
ls backend/outputs/*_page_*.png
```

---

## 🔍 Quick Diagnostics

### Check Tesseract
```bash
tesseract --version
```

### Check Server Status
```bash
curl http://localhost:8000/health
```

### Check OCR Health
```bash
curl http://localhost:8000/api/test/ocr-health
```

---

## 🐛 Quick Fixes

### Server won't start
```bash
# Check if port is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F
```

### Tesseract not found
```bash
# Windows: Download and install
# https://github.com/UB-Mannheim/tesseract/wiki

# Mac
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr
```

### Import errors
```bash
# Ensure you're in backend directory
cd backend
python -c "from main import app; print('OK')"
```

---

## 📊 Expected Results

### Phase 1 (File Handling)
- ✅ Files saved to uploads/
- ✅ PDFs converted to images
- ✅ Unique filenames generated

### Phase 2 (OCR)
- ✅ Images preprocessed
- ✅ Text extracted
- ✅ OCR logs saved

### Full Pipeline
- ✅ Fields extracted (invoice #, dates, amounts)
- ✅ Validation performed
- ✅ JSON response returned

---

## 🎯 Test Checklist

- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] File upload works
- [ ] PDF conversion works
- [ ] Image preprocessing works
- [ ] OCR extraction works
- [ ] Text is readable in logs
- [ ] No crashes on invalid input

---

## 📞 Need Help?

### Documentation
- `PHASE1_FILE_HANDLING_COMPLETE.md`
- `PHASE2_OCR_COMPLETE.md`
- `BACKEND_COMPLETE.md`
- `TESTING_GUIDE.md`

### Logs
- Server logs: Console output
- Processing logs: `backend/logs/`
- OCR logs: `backend/outputs/`

---

**Quick testing made easy! 🚀**

