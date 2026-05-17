"""
Pipeline Test Script - Test the complete invoice processing pipeline
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check...")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload(file_path):
    """Test file upload endpoint"""
    print("\n" + "="*50)
    print(f"Testing Upload: {file_path}")
    print("="*50)
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success!")
            print(f"Document ID: {result.get('document_id')}")
            print(f"Invoice Count: {result.get('invoice_count')}")
            print(f"Processing Time: {result.get('processing_time')}s")
            
            if result.get('invoices'):
                invoice = result['invoices'][0]
                print(f"\nExtracted Data:")
                print(f"  Invoice Number: {invoice.get('invoice_number')}")
                print(f"  Seller: {invoice.get('seller_name')}")
                print(f"  Buyer: {invoice.get('buyer_name')}")
                print(f"  Total: ₹{invoice.get('total_amount')}")
            
            if result.get('validation'):
                val = result['validation']
                print(f"\nValidation:")
                print(f"  Status: {val.get('validation_status')}")
                print(f"  Valid: {val.get('is_valid')}")
                if val.get('errors'):
                    print(f"  Errors: {val.get('errors')}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("  InvoiceIQ Backend Pipeline Test")
    print("  Member 2: Backend Engineer")
    print("="*50)
    
    # Test 1: Health Check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ Health check failed. Is the server running?")
        print("Start server with: python start_server.py")
        return
    
    print("\n✅ Health check passed!")
    
    # Test 2: Upload
    print("\n" + "="*50)
    print("Upload Test")
    print("="*50)
    print("\nTo test upload, place a sample invoice in backend/samples/")
    print("Then run: python test_pipeline.py <path_to_invoice>")
    
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        test_upload(file_path)
    else:
        print("\nUsage: python test_pipeline.py <invoice_file>")
        print("Example: python test_pipeline.py samples/invoice.jpg")
    
    print("\n" + "="*50)
    print("Testing Complete!")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
