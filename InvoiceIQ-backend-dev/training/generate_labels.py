import os
import json
import requests
from pathlib import Path

# API URL
API_URL = "http://127.0.0.1:8000/api/upload"

# Dataset folders
PDF_FOLDER = "../dataset/pdfs"
LABEL_FOLDER = "../dataset/labels"

# Create labels folder
os.makedirs(LABEL_FOLDER, exist_ok=True)

# Get all PDF files
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

print(f"Found {len(pdf_files)} PDF files")

for pdf_file in pdf_files:

    pdf_path = os.path.join(PDF_FOLDER, pdf_file)

    print(f"\nProcessing: {pdf_file}")

    try:

        with open(pdf_path, "rb") as f:

            files = {
                "file": (pdf_file, f, "application/pdf")
            }

            response = requests.post(API_URL, files=files)

        data = response.json()

        # Check invoices exist
        if "invoices" in data and len(data["invoices"]) > 0:

            invoice = data["invoices"][0]

            # Extract only needed fields
            label_data = {
                "invoice_number": invoice.get("invoice_number"),
                "seller_name": invoice.get("seller_name"),
                "buyer_name": invoice.get("buyer_name"),
                "date": invoice.get("date"),
                "subtotal": invoice.get("subtotal"),
                "tax_amount": invoice.get("tax_amount"),
                "total_amount": invoice.get("total_amount")
            }

            # JSON filename
            json_filename = Path(pdf_file).stem + ".json"

            json_path = os.path.join(LABEL_FOLDER, json_filename)

            # Save JSON
            with open(json_path, "w") as json_file:
                json.dump(label_data, json_file, indent=4)

            print(f"Saved: {json_filename}")

        else:
            print("No invoice data extracted")

    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

print("\nLabel generation completed")