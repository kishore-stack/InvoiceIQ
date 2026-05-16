# InvoiceOCR Frontend - Member 1

> **Professional AI-Powered Invoice Processing System - Frontend Application**

This is the complete frontend implementation for the InvoiceOCR system, built as part of a 3-member team project where this represents **Member 1's responsibility** - the entire UI/UX development.

---

## 📋 Project Overview

InvoiceOCR is an intelligent invoice processing system that uses AI/OCR to automatically extract and validate invoice data. This frontend application provides a modern, intuitive interface for users to upload invoices and view processed results.

### Team Structure

- **Member 1 (This Repository)**: Frontend Development (React + Tailwind)
- **Member 2**: Backend + AI/OCR Engine (FastAPI + Tesseract + ML)
- **Member 3**: Deployment + Database + DevOps (Vercel + Render + MongoDB)

---

## 🚀 Tech Stack

| Purpose | Technology |
|---------|-----------|
| Frontend Framework | React 19.2.6 |
| Build Tool | Vite 7.3.2 |
| Styling | Tailwind CSS 4.1.17 |
| Routing | React Router DOM 7.1.1 |
| HTTP Client | Axios 1.7.9 |
| Icons | Lucide React 0.469.0 |
| Language | JavaScript (JSX) |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.jsx       # Main navigation bar
│   │   ├── UploadBox.jsx    # Drag-and-drop file upload
│   │   ├── InvoiceCard.jsx  # Invoice list card component
│   │   ├── ResultTable.jsx  # Line items table display
│   │   └── ValidationBox.jsx # Validation status display
│   │
│   ├── pages/               # Application pages
│   │   ├── Home.jsx         # Upload page
│   │   ├── Dashboard.jsx    # Invoice list & management
│   │   ├── InvoiceDetails.jsx # Detailed invoice view
│   │   └── ErrorPage.jsx    # Error handling page
│   │
│   ├── services/            # API services
│   │   └── api.js           # Backend API integration
│   │
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # Application entry point
│   └── index.css            # Global styles
│
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
└── README.md                # This file
```

---

## 🎨 Features

### 1. Home Page - Upload Interface
- ✅ Modern drag-and-drop file upload
- ✅ Multiple file selection support
- ✅ File preview (images)
- ✅ Upload progress indicator
- ✅ Real-time upload status
- ✅ File validation (images & PDFs only)
- ✅ File size display
- ✅ Success/error notifications

### 2. Dashboard - Invoice Management
- ✅ Grid layout of processed invoices
- ✅ Search functionality (by invoice number, seller, buyer)
- ✅ Filter by validation status (All, Valid, Need Review)
- ✅ Statistics cards (Total, Valid, Review)
- ✅ Refresh functionality
- ✅ Delete invoices
- ✅ Quick view invoice details
- ✅ Loading states
- ✅ Empty state handling

### 3. Invoice Details Page
- ✅ Comprehensive invoice information display
- ✅ Seller and buyer details
- ✅ Line items table with calculations
- ✅ Financial summary (subtotal, tax, discount, total)
- ✅ Validation status and errors
- ✅ Confidence score visualization
- ✅ Multiple invoices per document support
- ✅ Print/export functionality
- ✅ Delete functionality
- ✅ Raw OCR text view (debugging)

### 4. Error Page
- ✅ User-friendly error messages
- ✅ Different error types (404, 500, OCR failure, network, file errors)
- ✅ Actionable suggestions
- ✅ Navigation options
- ✅ Refresh capability

---

## 🔌 API Integration

The frontend integrates with the following backend API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload invoice file(s) for processing |
| GET | `/invoice/{id}` | Get specific invoice details |
| GET | `/history` | Get all processed invoices |
| DELETE | `/invoice/{id}` | Delete specific invoice |

### API Configuration

The API base URL can be configured via environment variable:

```bash
VITE_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

---

## 🛠️ Installation & Setup

### Prerequisites

- Node.js 18+ and npm
- Backend server running (Member 2's responsibility)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (optional):**
   Create a `.env` file in the root directory:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open in browser:**
   Navigate to `http://localhost:5173`

---

## 📦 Build & Deployment

### Production Build

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deployment (Member 3's Responsibility)

The built application will be deployed to **Vercel** by Member 3.

---

## 🎯 Usage Guide

### Uploading Invoices

1. Navigate to the home page
2. Drag and drop invoice files or click "Select Files"
3. Select one or multiple invoice files (JPG, PNG, PDF)
4. Review selected files in the preview
5. Click "Upload & Process Invoices"
6. Wait for processing (progress bar shown)
7. Automatically redirected to dashboard upon success

### Viewing Invoices

1. Navigate to Dashboard
2. View all processed invoices in grid layout
3. Use search bar to find specific invoices
4. Filter by validation status
5. Click "View Details" on any invoice card

### Managing Invoices

1. Click on an invoice to view full details
2. Review validation status and errors
3. Examine line items and calculations
4. Print or export data if needed
5. Delete invoice if necessary

---

## 🎨 UI/UX Highlights

### Design Principles

- **Modern & Clean**: Minimalist design with focus on content
- **Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Accessible**: Proper color contrast and semantic HTML
- **Intuitive**: Clear navigation and user flows
- **Fast**: Optimized loading and smooth transitions

### Color Palette

- Primary: Blue (#2563eb) to Indigo (#4338ca)
- Success: Green (#22c55e)
- Warning: Yellow (#eab308)
- Error: Red (#ef4444)
- Neutral: Gray shades

### Components

- **Cards**: Elevated with subtle shadows and hover effects
- **Buttons**: Gradient backgrounds with smooth transitions
- **Forms**: Clean inputs with focus states
- **Tables**: Responsive with alternating row colors
- **Badges**: Color-coded status indicators

---

## 🔍 Component Documentation

### UploadBox Component

Handles file upload with drag-and-drop functionality.

**Props:**
- `onUpload(files)`: Callback when files are uploaded
- `isLoading`: Boolean to show loading state

**Features:**
- Drag and drop support
- Multiple file selection
- File type validation
- Image preview
- File size display
- Remove files before upload

### InvoiceCard Component

Displays invoice summary in grid layout.

**Props:**
- `invoice`: Invoice data object
- `onDelete(id)`: Callback for delete action

**Features:**
- Status badge (Valid/Review)
- Key information display
- Confidence score bar
- Quick actions

### ResultTable Component

Displays line items in tabular format with calculations.

**Props:**
- `items`: Array of line item objects

**Features:**
- Responsive table
- Automatic calculations
- Subtotal, tax, discount summaries
- Grand total

### ValidationBox Component

Shows validation status and errors.

**Props:**
- `validationData`: Validation result object

**Features:**
- Status indicator (success/warning/error)
- Confidence score visualization
- Error list
- Warning list
- Validation details

---

## 🧪 Testing Locally

### With Mock Data

If backend is not available, you can test the UI by:

1. Starting the dev server
2. Navigating through pages
3. UI will show appropriate error messages for failed API calls

### With Backend

1. Ensure backend is running at `http://localhost:8000`
2. Start frontend: `npm run dev`
3. Upload test invoices
4. Verify data processing and display

---

## 📝 Development Notes

### State Management

- Uses React's built-in `useState` and `useEffect` hooks
- No external state management library needed
- Component-level state for simplicity

### Routing

- Client-side routing with React Router
- 404 error handling
- Nested routes for invoice details

### Error Handling

- Try-catch blocks for API calls
- User-friendly error messages
- Fallback UI for errors
- Loading states for async operations

### Performance

- Lazy loading for images
- Debounced search (future enhancement)
- Optimized re-renders
- Vite's fast HMR

---

## 🚫 What This Frontend Does NOT Handle

As per team division, this frontend **ONLY** handles UI/UX and **DOES NOT**:

- ❌ OCR processing
- ❌ Machine learning
- ❌ Image preprocessing
- ❌ Regex extraction
- ❌ Validation logic
- ❌ Database operations
- ❌ File storage

All processing is delegated to the backend API (Member 2's responsibility).

---

## 🤝 Integration with Other Members

### With Member 2 (Backend Engineer)

**Required from Backend:**

1. **POST /upload endpoint**
   - Accepts multipart/form-data
   - Returns: `{ document_id, invoice_count, invoices: [...] }`

2. **GET /invoice/{id} endpoint**
   - Returns detailed invoice data
   - Includes validation status and line items

3. **GET /history endpoint**
   - Returns array of all invoices
   - Supports pagination (future)

4. **DELETE /invoice/{id} endpoint**
   - Deletes invoice and returns success

**JSON Response Format Expected:**

```json
{
  "document_id": "DOC101",
  "invoice_count": 1,
  "invoices": [
    {
      "invoice_number": "INV-001",
      "seller_name": "ABC Pvt Ltd",
      "buyer_name": "XYZ Ltd",
      "total_amount": 1200.00,
      "validation_status": "valid",
      "validation_errors": [],
      "confidence_score": 95,
      "line_items": [...]
    }
  ]
}
```

### With Member 3 (DevOps Engineer)

**Required for Deployment:**

1. Build the frontend: `npm run build`
2. Deploy `dist/` folder to Vercel
3. Set environment variable: `VITE_API_URL` pointing to backend
4. Configure CORS on backend to allow frontend domain

---

## 📚 Dependencies

### Production Dependencies

```json
{
  "react": "19.2.6",
  "react-dom": "19.2.6",
  "react-router-dom": "7.1.1",
  "axios": "1.7.9",
  "lucide-react": "0.469.0",
  "clsx": "2.1.1",
  "tailwind-merge": "3.4.0"
}
```

### Development Dependencies

```json
{
  "@vitejs/plugin-react": "5.1.1",
  "@tailwindcss/vite": "4.1.17",
  "tailwindcss": "4.1.17",
  "vite": "7.3.2",
  "typescript": "5.9.3"
}
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Backend Connection Error**
- Ensure backend is running at the correct URL
- Check CORS configuration on backend
- Verify `VITE_API_URL` in `.env`

**2. File Upload Fails**
- Check file size (must be < 10MB)
- Verify file type (JPG, PNG, PDF only)
- Check backend error logs

**3. Blank Dashboard**
- Check browser console for errors
- Verify `/history` endpoint returns data
- Check network tab in DevTools

**4. Build Errors**
- Run `npm install` to ensure dependencies
- Clear `node_modules` and reinstall
- Check Node.js version (18+)

---

## 📄 License

This project is part of an academic/team project. All rights reserved.

---

## 👥 Team Members

- **Member 1 (This)**: Frontend Engineer - Complete UI/UX
- **Member 2**: Backend + AI/OCR Engineer
- **Member 3**: Deployment + DevOps Engineer

---

## 📞 Support

For issues or questions related to the frontend:
1. Check this README
2. Review component documentation above
3. Check browser console for errors
4. Verify API integration with backend team

---

## ✅ Checklist for Member 1

- [x] UploadBox component with drag-drop
- [x] InvoiceCard component
- [x] ResultTable component
- [x] ValidationBox component
- [x] Navbar component
- [x] Home page with upload
- [x] Dashboard page with filters
- [x] Invoice details page
- [x] Error page
- [x] API service integration
- [x] Responsive design
- [x] Loading states
- [x] Error handling
- [x] Professional UI/UX
- [x] README documentation

---

**Built with ❤️ by Member 1 - Frontend Engineer**
