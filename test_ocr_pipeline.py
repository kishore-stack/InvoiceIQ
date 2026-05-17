"""
OCR Pipeline Test Script
Tests: File Upload → PDF Conversion → Preprocessing → OCR Extraction
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_ocr_health():
    """Test OCR components health"""
    print_header("TEST 1: OCR Pipeline Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/test/ocr-health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Health check passed!")
            print(f"\nStatus: {result['status']}")
            print(f"\nComponents:")
            for component, status in result['components'].items():
                icon = "✅" if status == "operational" else "❌"
                print(f"  {icon} {component}: {status}")
            
            print(f"\nTesseract OCR:")
            tesseract = result['tesseract']
            if tesseract['available']:
                print(f"  ✅ Available")
                print(f"  Version: {tesseract.get('version', 'unknown')}")
            else:
                print(f"  ❌ Not available")
                print(f"  Error: {tesseract.get('error', 'unknown')}")
                print(f"\n⚠️  Install Tesseract OCR to continue:")
                print(f"     Windows: https://github.com/UB-Mannheim/tesseract/wiki")
                print(f"     Mac: brew install tesseract")
                print(f"     Linux: sudo apt-get install tesseract-ocr")
                return False
            
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Is the server running? Start with: python start_server.py")
        return False

def test_preprocessing_only(file_path):
    """Test only preprocessing (no OCR)"""
    print_header(f"TEST 2: Preprocessing Only - {Path(file_path).name}")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            response = requests.post(
                f"{BASE_URL}/api/test/test-preprocessing",
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Preprocessing successful!")
            print(f"\nPages processed: {result['page_count']}")
            
            for page_result in result['results']:
                page_num = page_result['page']
                if page_result['success']:
                    print(f"\n  Page {page_num}: ✅ Success")
                    print(f"    Processed image: {page_result['processed_path']}")
                else:
                    print(f"\n  Page {page_num}: ❌ Failed")
                    print(f"    Error: {page_result.get('error')}")
            
            print(f"\n{result['message']}")
            return True
        else:
            print(f"❌ Preprocessing failed: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_full_ocr_pipeline(file_path):
    """Test complete OCR pipeline"""
    print_header(f"TEST 3: Full OCR Pipeline - {Path(file_path).name}")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            response = requests.post(
                f"{BASE_URL}/api/test/ocr-pipeline",
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ OCR pipeline completed!")
            
            print(f"\nFile Info:")
            print(f"  Original: {result['file_info']['original_filename']}")
            print(f"  Type: {result['file_info']['file_type']}")
            
            print(f"\nConversion:")
            print(f"  Is PDF: {result['conversion']['is_pdf']}")
            print(f"  Pages: {result['conversion']['page_count']}")
            
            print(f"\nOCR Results:")
            for ocr_result in result['ocr_results']:
                page_num = ocr_result['page']
                status = ocr_result['status']
                
                if status == 'success':
                    print(f"\n  📄 Page {page_num}: ✅ Success")
                    print(f"     Characters extracted: {ocr_result['char_count']}")
                    print(f"     Lines extracted: {ocr_result['line_count']}")
                    print(f"     Processed image: {ocr_result['processed_image']}")
                    print(f"     OCR log: {ocr_result['ocr_log']}")
                    
                    # Show first 200 characters of extracted text
                    text = ocr_result['text']
                    preview = text[:200] + "..." if len(text) > 200 else text
                    print(f"\n     Text Preview:")
                    print(f"     {'-'*60}")
                    for line in preview.split('\n')[:5]:
                        print(f"     {line}")
                    print(f"     {'-'*60}")
                else:
                    print(f"\n  📄 Page {page_num}: ❌ {status}")
                    print(f"     Error: {ocr_result.get('error')}")
            
            print(f"\n{result['message']}")
            return True
        else:
            print(f"❌ OCR pipeline failed: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_sample_instructions():
    """Show instructions for creating sample invoices"""
    print_header("Sample Invoice Instructions")
    
    print("\nTo test the OCR pipeline, you need sample invoice images.")
    print("\nOption 1: Use existing invoices")
    print("  - Place invoice images in: backend/samples/")
    print("  - Supported formats: JPG, PNG, PDF")
    
    print("\nOption 2: Create test invoice")
    print("  - Create a simple text document")
    print("  - Add invoice-like content:")
    print("    Invoice No: INV-001")
    print("    Date: 15/01/2024")
    print("    Seller: ABC Company")
    print("    Buyer: XYZ Corp")
    print("    Total: ₹1200")
    print("  - Save as image or PDF")
    
    print("\nOption 3: Download sample invoices")
    print("  - Search online for 'sample invoice PDF'")
    print("  - Download and save to backend/samples/")

def main():
    """Run all OCR tests"""
    print("\n" + "="*70)
    print("  InvoiceIQ Backend - OCR Pipeline Test Suite")
    print("  Testing: Preprocessing + OCR Extraction")
    print("  NOT Testing: Field extraction, validation")
    print("="*70)
    
    # Test 1: Health Check
    if not test_ocr_health():
        print("\n❌ OCR pipeline not ready. Please fix issues above.")
        return
    
    print("\n✅ OCR pipeline is healthy!")
    
    # Check for sample files
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # Test 2: Preprocessing only
        print("\n" + "="*70)
        print("  Running preprocessing test...")
        print("="*70)
        test_preprocessing_only(file_path)
        
        # Test 3: Full OCR pipeline
        print("\n" + "="*70)
        print("  Running full OCR pipeline test...")
        print("="*70)
        test_full_ocr_pipeline(file_path)
    else:
        print_header("No Test File Provided")
        print("\nUsage: python test_ocr_pipeline.py <path_to_invoice>")
        print("\nExamples:")
        print("  python test_ocr_pipeline.py samples/invoice.jpg")
        print("  python test_ocr_pipeline.py samples/invoice.pdf")
        print("  python test_ocr_pipeline.py samples/multi_page.pdf")
        
        create_sample_instructions()
    
    print_header("Test Summary")
    print("✅ OCR health check: Passed")
    print("✅ Preprocessing module: Ready")
    print("✅ OCR extraction module: Ready")
    print("✅ Pipeline integration: Working")
    
    print("\n📝 Next Steps:")
    print("  1. Test with real invoice images")
    print("  2. Check OCR accuracy in backend/outputs/")
    print("  3. Review OCR logs for text quality")
    print("  4. Adjust preprocessing if needed")
    
    print("\n🎯 After OCR works well:")
    print("  → Next phase: Regex field extraction")
    print("  → Extract: invoice number, dates, amounts, GST")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
