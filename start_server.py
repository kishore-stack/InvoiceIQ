"""
Quick Start Script - InvoiceIQ Backend Server
Run this to start the backend server
"""

import os
import sys

def main():
    print("\n" + "="*50)
    print("  InvoiceIQ Backend Server")
    print("  Member 2: Backend Engineer")
    print("="*50 + "\n")
    
    print("Starting FastAPI server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start uvicorn server
    os.system("uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()
