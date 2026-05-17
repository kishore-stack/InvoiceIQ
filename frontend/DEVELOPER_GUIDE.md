# Developer Guide - InvoiceOCR Frontend

## Member 1's Complete Implementation Guide

This guide provides detailed information about the frontend architecture, component structure, and development practices.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           User Interface                │
│  (React Components + Tailwind CSS)      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         React Router                    │
│  (Client-side Navigation)               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         API Service Layer               │
│  (Axios HTTP Client)                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Backend REST API                   │
│  (Member 2's FastAPI Server)            │
└─────────────────────────────────────────┘
```

---

## Component Architecture

### Component Hierarchy

```
App
├── Navbar (Global)
└── Routes
    ├── Home
    │   └── UploadBox
    │
    ├── Dashboard
    │   ├── InvoiceCard (Multiple)
    │   └── Search/Filter Controls
    │
    ├── InvoiceDetails
    │   ├── ValidationBox
    │   └── ResultTable
    │
    └── ErrorPage
```

---

## Component Details

### 1. Navbar Component

**Location:** `src/components/Navbar.jsx`

**Purpose:** Global navigation bar

**Features:**
- Logo and branding
- Navigation links (Home, Dashboard)
- Active link highlighting
- Responsive mobile menu
- System status indicator

**Props:** None (uses React Router's `useLocation`)

**State:** 
- `location` - current route from React Router

**Key Functions:**
- `isActive(path)` - checks if route is active

**Styling:**
- Sticky positioning
- Gradient logo
- Border-bottom separator
- Mobile-friendly hamburger menu

---

### 2. UploadBox Component

**Location:** `src/components/UploadBox.jsx`

**Purpose:** File upload with drag-and-drop

**Props:**
```javascript
{
  onUpload: (files) => void,  // Callback when upload initiated
  isLoading: boolean           // Shows loading state
}
```

**State:**
```javascript
{
  dragActive: boolean,         // True when dragging over
  selectedFiles: File[],       // Array of selected files
  previewUrls: string[]        // Object URLs for previews
}
```

**Key Functions:**
- `handleDrag(e)` - Manages drag events
- `handleDrop(e)` - Processes dropped files
- `handleChange(e)` - Processes selected files
- `handleFiles(files)` - Validates and sets files
- `removeFile(index)` - Removes a file from selection
- `handleUpload()` - Triggers upload callback
- `getFileIcon(file)` - Returns appropriate icon
- `formatFileSize(bytes)` - Formats file size display

**Validation:**
- Only accepts image/* and application/pdf
- Shows alert for invalid files

**Memory Management:**
- Properly revokes object URLs to prevent memory leaks

---

### 3. InvoiceCard Component

**Location:** `src/components/InvoiceCard.jsx`

**Purpose:** Display invoice summary in grid

**Props:**
```javascript
{
  invoice: {
    document_id: string,
    invoice_count: number,
    validation_status: string,
    is_valid: boolean,
    validation_errors: string[],
    confidence_score: number,
    invoices: Invoice[]
  },
  onDelete: (id) => void
}
```

**Features:**
- Status badge (Valid/Review)
- Company information
- Financial summary
- Confidence score bar
- Action buttons (View, Delete)

**Styling:**
- Hover effects
- Gradient backgrounds
- Card elevation
- Responsive grid layout

---

### 4. ResultTable Component

**Location:** `src/components/ResultTable.jsx`

**Purpose:** Display line items with calculations

**Props:**
```javascript
{
  items: LineItem[]
}
```

**LineItem Structure:**
```javascript
{
  description: string,
  quantity: number,
  unit_price: number,
  price: number,
  tax: number,
  discount: number,
  total: number
}
```

**Calculations:**
- Subtotal: Sum of (price × quantity)
- Total Tax: Sum of all tax amounts
- Total Discount: Sum of all discounts
- Grand Total: Subtotal + Tax - Discount

**Features:**
- Responsive table
- Auto-scrolling on mobile
- Striped rows for readability
- Summary section
- Empty state handling

---

### 5. ValidationBox Component

**Location:** `src/components/ValidationBox.jsx`

**Purpose:** Display validation status and errors

**Props:**
```javascript
{
  validationData: {
    is_valid: boolean,
    validation_status: string,
    validation_errors: string[],
    validation_warnings: string[],
    confidence_score: number,
    validation_details: object
  }
}
```

**Status Types:**
- **Success:** All validations passed
- **Error:** Validation failures found
- **Warning:** Minor issues detected
- **Info:** Basic processing complete

**Features:**
- Color-coded status cards
- Confidence score visualization
- Error list display
- Warning list display
- Validation details grid

**Styling:**
- Dynamic background colors
- Icon indicators
- Progress bars
- Collapsible sections

---

## Page Components

### 1. Home Page

**Location:** `src/pages/Home.jsx`

**Purpose:** Upload interface and hero section

**State:**
```javascript
{
  isLoading: boolean,
  uploadProgress: number,
  uploadStatus: 'success' | 'error' | null,
  uploadResult: object,
  errorMessage: string
}
```

**Flow:**
1. User selects/drops files
2. Files validated and previewed
3. User clicks upload
4. Progress shown (0-100%)
5. Success → redirect to dashboard
6. Error → show error message

**API Call:**
```javascript
api.uploadInvoice(files, (progress) => {
  setUploadProgress(progress);
})
```

**Features:**
- Hero section with features
- Drag-and-drop upload
- Progress indicator
- Success notification
- Error handling
- Auto-redirect after success

---

### 2. Dashboard Page

**Location:** `src/pages/Dashboard.jsx`

**Purpose:** Invoice list and management

**State:**
```javascript
{
  invoices: Invoice[],
  filteredInvoices: Invoice[],
  isLoading: boolean,
  searchQuery: string,
  filterStatus: 'all' | 'valid' | 'review',
  error: string
}
```

**Features:**
- Statistics cards (Total, Valid, Review)
- Search by invoice number, seller, buyer
- Filter by validation status
- Refresh functionality
- Delete invoices
- Grid layout
- Empty states

**Effects:**
- Fetch invoices on mount
- Re-filter on search/filter change

**Filtering Logic:**
1. Search: Case-insensitive substring match
2. Status filter: 
   - All: Show everything
   - Valid: `is_valid && !validation_errors.length`
   - Review: `!is_valid || validation_errors.length > 0`

---

### 3. Invoice Details Page

**Location:** `src/pages/InvoiceDetails.jsx`

**Purpose:** Detailed invoice view

**State:**
```javascript
{
  invoice: Invoice,
  isLoading: boolean,
  error: string
}
```

**URL Parameter:**
- `id` - Document ID from route

**Sections:**
1. Header with back button
2. Validation status box
3. Invoice information
4. Seller/Buyer details
5. Line items table
6. Financial summary
7. Raw OCR text (collapsible)

**Features:**
- Multi-invoice support (if document has multiple)
- Export/Print functionality
- Delete functionality
- Navigation breadcrumbs
- Loading states
- Error handling

---

### 4. Error Page

**Location:** `src/pages/ErrorPage.jsx`

**Purpose:** Handle errors and 404s

**Features:**
- Detects error type (404, 500, OCR, network, file)
- Customized message per error type
- Action buttons (Go Home, Refresh)
- Helpful suggestions
- Technical details display

**Error Detection:**
```javascript
getErrorDetails() {
  if (error?.status === 404) return {...}
  if (error?.message?.includes('OCR')) return {...}
  // etc.
}
```

---

## API Service

**Location:** `src/services/api.js`

### Configuration

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Methods

#### 1. uploadInvoice
```javascript
api.uploadInvoice(files, onUploadProgress)
```
- **Accepts:** File or FileList
- **Returns:** Promise with upload result
- **Features:** Progress callback support

#### 2. getInvoice
```javascript
api.getInvoice(id)
```
- **Accepts:** Document ID string
- **Returns:** Promise with invoice data

#### 3. getHistory
```javascript
api.getHistory(params)
```
- **Accepts:** Query parameters (optional)
- **Returns:** Promise with invoice list

#### 4. deleteInvoice
```javascript
api.deleteInvoice(id)
```
- **Accepts:** Document ID string
- **Returns:** Promise with success message

### Error Handling

All API methods use try-catch and return errors to the caller:

```javascript
try {
  const response = await api.uploadInvoice(files);
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error(error.response.data);
  } else if (error.request) {
    // No response received
    console.error('No response from server');
  } else {
    // Request setup error
    console.error(error.message);
  }
}
```

---

## Routing

**Implementation:** React Router v7

### Routes

```javascript
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/invoice/:id" element={<InvoiceDetails />} />
  <Route path="*" element={<ErrorPage />} />
</Routes>
```

### Navigation Methods

**Programmatic:**
```javascript
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/dashboard');
```

**Declarative:**
```javascript
import { Link } from 'react-router-dom';
<Link to="/dashboard">Go to Dashboard</Link>
```

### Route Parameters

```javascript
import { useParams } from 'react-router-dom';
const { id } = useParams();
```

---

## Styling System

### Tailwind CSS Classes

**Common Patterns:**

**Buttons:**
```jsx
className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
```

**Cards:**
```jsx
className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-lg transition-shadow"
```

**Inputs:**
```jsx
className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
```

**Gradients:**
```jsx
className="bg-gradient-to-r from-blue-600 to-indigo-700"
```

### Custom CSS

**Animations:**
```css
.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Scrollbar:**
- Custom styled scrollbar for better UX
- Applied globally

---

## State Management

### Strategy

- **No external state library** (Redux, Zustand, etc.)
- Uses React's built-in hooks
- Component-level state for UI
- Server state managed via API calls

### Hooks Used

**useState:**
```javascript
const [data, setData] = useState(initialValue);
```

**useEffect:**
```javascript
useEffect(() => {
  fetchData();
}, [dependency]);
```

**useNavigate:**
```javascript
const navigate = useNavigate();
navigate('/path');
```

**useParams:**
```javascript
const { id } = useParams();
```

**useLocation:**
```javascript
const location = useLocation();
const isActive = location.pathname === '/path';
```

---

## Performance Optimizations

### 1. Lazy Loading

Currently not implemented but can add:
```javascript
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

### 2. Memoization

For expensive calculations:
```javascript
const total = useMemo(() => {
  return items.reduce((sum, item) => sum + item.price, 0);
}, [items]);
```

### 3. Debouncing

For search input (future enhancement):
```javascript
const debouncedSearch = useDebounce(searchQuery, 300);
```

### 4. Image Optimization

- Preview images are object URLs
- Properly revoked to prevent memory leaks
- Lazy loading for dashboard cards

---

## Error Handling Strategy

### Levels of Error Handling

**1. API Level:**
```javascript
try {
  const response = await api.uploadInvoice(files);
  return response.data;
} catch (error) {
  throw error; // Pass to component
}
```

**2. Component Level:**
```javascript
try {
  await handleUpload();
  setUploadStatus('success');
} catch (err) {
  const detail = err.response?.data?.detail;

  if (Array.isArray(detail)) {
    setError(detail.map((e) => e.msg).join(", "));
  } else if (typeof detail === "string") {
    setError(detail);
  } else {
    setError("Upload failed. Please check the file and try again.");
  }
}
```

**3. User Level:**
- Display user-friendly messages
- Provide actionable suggestions
- Show technical details in development

### Error Types

1. **Network Errors:** "Backend not responding"
2. **Validation Errors:** "Invalid file format"
3. **OCR Errors:** "Unable to process image"
4. **404 Errors:** "Resource not found"
5. **Server Errors:** "Internal server error"

---

## Testing Recommendations

### Unit Tests (Not Implemented)

```javascript
// Example with React Testing Library
import { render, screen } from '@testing-library/react';
import InvoiceCard from './components/InvoiceCard';

test('renders invoice number', () => {
  render(<InvoiceCard invoice={mockData} />);
  expect(screen.getByText('INV-001')).toBeInTheDocument();
});
```

### Integration Tests

Test user flows:
1. Upload → Dashboard → Details
2. Search and filter functionality
3. Delete functionality

### Manual Testing Checklist

- [ ] Upload single file
- [ ] Upload multiple files
- [ ] Drag and drop upload
- [ ] Search invoices
- [ ] Filter by status
- [ ] View invoice details
- [ ] Delete invoice
- [ ] Navigate between pages
- [ ] Mobile responsiveness
- [ ] Error scenarios

---

## Accessibility

### Implemented Features

- Semantic HTML elements
- Alt text for images
- Proper heading hierarchy
- Keyboard navigation support
- Focus states on interactive elements
- ARIA labels where needed

### Future Enhancements

- Screen reader testing
- Keyboard shortcuts
- High contrast mode
- Focus trap in modals
- Skip to content link

---

## Browser Support

### Supported Browsers

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

### Polyfills

Not needed - Vite handles modern syntax transpilation.

---

## Development Workflow

### 1. Start Development

```bash
npm run dev
```

### 2. Make Changes

- Edit component files
- Hot Module Replacement (HMR) updates instantly
- Check browser console for errors

### 3. Test Locally

- Test all user flows
- Check responsive design
- Verify error handling

### 4. Build for Production

```bash
npm run build
```

### 5. Preview Build

```bash
npm run preview
```

---

## Deployment Process (Member 3)

### Build Command

```bash
npm run build
```

### Output Directory

```
dist/
```

### Environment Variables

Set on Vercel:
- `VITE_API_URL` = Backend URL

### Build Settings (Vercel)

```
Framework: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Node Version: 18.x
```

---

## Troubleshooting Guide

### Issue: Port 5173 already in use

**Solution:**
```bash
lsof -ti:5173 | xargs kill -9
# Or use different port
npm run dev -- --port 3000
```

### Issue: Module not found

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Build fails

**Solution:**
```bash
# Clear cache
rm -rf dist
# Check for TypeScript errors
npm run build
```

### Issue: Backend connection fails

**Solutions:**
1. Check backend is running
2. Verify CORS settings
3. Check `VITE_API_URL` in .env
4. Check browser network tab

### Issue: Images not displaying

**Solutions:**
1. Check file paths
2. Verify object URLs are created
3. Check for memory leaks (revoke URLs)

---

## Code Style Guide

### File Naming

- Components: PascalCase.jsx (e.g., `InvoiceCard.jsx`)
- Pages: PascalCase.jsx (e.g., `Dashboard.jsx`)
- Services: camelCase.js (e.g., `api.js`)
- Styles: kebab-case.css (e.g., `index.css`)

### Component Structure

```javascript
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const ComponentName = ({ prop1, prop2 }) => {
  // State
  const [state, setState] = useState(initialValue);
  
  // Hooks
  const navigate = useNavigate();
  
  // Effects
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  // Handlers
  const handleEvent = () => {
    // Logic
  };
  
  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
};

export default ComponentName;
```

### CSS Classes Order

1. Layout (flex, grid)
2. Sizing (w-, h-)
3. Spacing (p-, m-)
4. Typography (text-, font-)
5. Colors (bg-, text-)
6. Borders (border-)
7. Effects (shadow-, rounded-)
8. Transitions (transition-, hover:)

---

## Future Enhancements

### Potential Features

1. **Advanced Search:**
   - Date range filter
   - Amount range filter
   - Multi-field search

2. **Bulk Operations:**
   - Select multiple invoices
   - Bulk delete
   - Bulk export

3. **Data Visualization:**
   - Charts for invoice trends
   - Monthly summaries
   - Seller/buyer analytics

4. **User Preferences:**
   - Dark mode
   - Theme customization
   - Table column preferences

5. **Offline Support:**
   - Service workers
   - Cached data
   - Offline queue

6. **Real-time Updates:**
   - WebSocket connection
   - Live processing status
   - Notifications

---

## Contact & Support

For frontend-related issues:
- Review this developer guide
- Check component documentation
- Test with mock data
- Verify API integration with backend team

---

**Last Updated:** January 2025
**Maintainer:** Member 1 - Frontend Engineer
**Version:** 1.0.0
