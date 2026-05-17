# Quick Reference Card

## 🚀 Quick Start

```bash
npm install           # Install dependencies
npm run dev           # Start dev server (http://localhost:5173)
npm run build         # Build for production
npm run preview       # Preview production build
```

---

## 📁 File Structure

```
src/
├── components/       # UI Components
├── pages/           # Route Pages
├── services/        # API Service
├── App.jsx          # Main App
└── main.jsx         # Entry Point
```

---

## 🔗 Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | Home | Upload interface |
| `/dashboard` | Dashboard | Invoice list |
| `/invoice/:id` | InvoiceDetails | Detailed view |
| `*` | ErrorPage | 404 handler |

---

## 🎨 Components

| Component | Props | Purpose |
|-----------|-------|---------|
| `Navbar` | - | Global navigation |
| `UploadBox` | `onUpload`, `isLoading` | File upload |
| `InvoiceCard` | `invoice`, `onDelete` | Invoice summary |
| `ResultTable` | `items` | Line items table |
| `ValidationBox` | `validationData` | Validation display |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload invoices |
| GET | `/invoice/{id}` | Get invoice |
| GET | `/history` | List all invoices |
| DELETE | `/invoice/{id}` | Delete invoice |

---

## 📦 Key Dependencies

```json
{
  "react": "19.2.6",
  "react-router-dom": "7.1.1",
  "axios": "1.7.9",
  "lucide-react": "0.469.0",
  "tailwindcss": "4.1.17"
}
```

---

## 🎯 API Usage

```javascript
import api from './services/api';

// Upload
await api.uploadInvoice(files, (progress) => {
  console.log(`${progress}%`);
});

// Get invoice
const invoice = await api.getInvoice('DOC101');

// Get history
const history = await api.getHistory();

// Delete
await api.deleteInvoice('DOC101');
```

---

## 🎨 Common CSS Patterns

**Button:**
```jsx
className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
```

**Card:**
```jsx
className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
```

**Input:**
```jsx
className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
```

---

## 🔧 Environment Variables

```bash
# .env
VITE_API_URL=http://localhost:8000
```

---

## 📱 Pages Overview

### Home
- Hero section
- File upload (drag & drop)
- Progress indicator
- Success/error handling

### Dashboard
- Statistics cards
- Search & filter
- Invoice grid
- Refresh & delete

### Invoice Details
- Full invoice data
- Validation status
- Line items table
- Print/export

### Error Page
- 404 handling
- Error messages
- Navigation options

---

## 🛠️ Common Tasks

**Add new component:**
```bash
touch src/components/NewComponent.jsx
```

**Add new page:**
```bash
touch src/pages/NewPage.jsx
```

**Install package:**
```bash
npm install package-name
```

**Update route:**
```jsx
// src/App.jsx
<Route path="/new" element={<NewPage />} />
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -ti:5173 \| xargs kill -9` |
| Dependencies error | `rm -rf node_modules && npm install` |
| Build fails | `rm -rf dist && npm run build` |
| API not connecting | Check backend is running + CORS |

---

## 📊 Invoice Data Structure

```javascript
{
  document_id: "DOC101",
  invoice_count: 1,
  validation_status: "valid",
  is_valid: true,
  validation_errors: [],
  confidence_score: 95.5,
  invoices: [
    {
      invoice_number: "INV-001",
      seller_name: "ABC Ltd",
      buyer_name: "XYZ Ltd",
      total_amount: 1200.00,
      line_items: [
        {
          description: "Item",
          quantity: 2,
          unit_price: 100,
          tax: 20,
          discount: 0,
          total: 240
        }
      ]
    }
  ]
}
```

---

## ✅ Testing Checklist

- [ ] Upload single file
- [ ] Upload multiple files
- [ ] Drag & drop works
- [ ] Search invoices
- [ ] Filter by status
- [ ] View details
- [ ] Delete invoice
- [ ] Mobile responsive
- [ ] Error handling
- [ ] Loading states

---

## 📚 Documentation Files

- `README.md` - Overview & setup
- `SETUP.md` - Quick setup guide
- `API_CONTRACT.md` - API specifications
- `DEVELOPER_GUIDE.md` - In-depth guide
- `QUICK_REFERENCE.md` - This file

---

## 🎯 Member Responsibilities

| Member | Responsibility |
|--------|---------------|
| **Member 1 (You)** | Frontend UI/UX |
| Member 2 | Backend + AI/OCR |
| Member 3 | Deployment + DevOps |

---

## 🚀 Deployment (Member 3)

**Build:**
```bash
npm run build
```

**Output:** `dist/`

**Platform:** Vercel

**Env Vars:**
- `VITE_API_URL` = Backend URL

---

## 📞 Quick Help

**Backend not responding?**
1. Check if running at `localhost:8000`
2. Verify CORS enabled
3. Check `.env` file

**Build errors?**
1. Clear cache: `rm -rf dist`
2. Reinstall: `rm -rf node_modules && npm install`
3. Check Node version: `node --version` (need 18+)

**UI not updating?**
1. Hard refresh: Ctrl+Shift+R
2. Clear browser cache
3. Restart dev server

---

**Keep this handy for quick reference! 🚀**
