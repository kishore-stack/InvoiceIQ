"""
Quick test script to verify FastAPI server setup
"""

import sys
sys.path.insert(0, '.')

try:
    from main import app
    print("✅ FastAPI app imported successfully")
    print("✅ Backend foundation is ready")
    print("\nTo run the server:")
    print("  uvicorn main:app --reload")
    print("\nThen visit:")
    print("  http://127.0.0.1:8000/docs")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
