# Quick Setup Guide - InvoiceOCR Frontend

## For Member 1 (You)

### Initial Setup

1. **Verify Node.js installation:**
   ```bash
   node --version  # Should be 18 or higher
   npm --version
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env to set your backend URL
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   Navigate to: `http://localhost:5173`

---

## Testing Without Backend

The frontend is fully functional and will show appropriate error messages if the backend is not available. You can:

- Navigate through all pages
- Test the UI/UX
- Upload files (will fail gracefully with error message)
- View the error page

---

## Testing With Backend (When Member 2 is Ready)

### Prerequisites

1. Member 2's backend must be running at `http://localhost:8000`
2. Backend must have CORS enabled for `http://localhost:5173`

### Steps

1. **Start backend first:**
   (Member 2's responsibility)
   ```bash
   # In backend directory
   uvicorn main:app --reload
   ```

2. **Start frontend:**
   ```bash
   npm run dev
   ```

3. **Test the flow:**
   - Upload an invoice on home page
   - View it in dashboard
   - Click to see details
   - Test delete functionality

---

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory.

To preview the production build:
```bash
npm run preview
```

---

## File Structure You Created

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx          ✓ Created
│   │   ├── UploadBox.jsx       ✓ Created
│   │   ├── InvoiceCard.jsx     ✓ Created
│   │   ├── ResultTable.jsx     ✓ Created
│   │   └── ValidationBox.jsx   ✓ Created
│   │
│   ├── pages/
│   │   ├── Home.jsx            ✓ Created
│   │   ├── Dashboard.jsx       ✓ Created
│   │   ├── InvoiceDetails.jsx  ✓ Created
│   │   └── ErrorPage.jsx       ✓ Created
│   │
│   ├── services/
│   │   └── api.js              ✓ Created
│   │
│   ├── App.jsx                 ✓ Created
│   ├── main.jsx                ✓ Created
│   └── index.css               ✓ Updated
│
├── .env.example                ✓ Created
├── README.md                   ✓ Created
└── SETUP.md                    ✓ This file
```

---

## Common Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install a new package
npm install package-name
```

---

## What to Share with Team

### With Member 2 (Backend):

Share the **API Contract** section from README.md:
- POST `/upload` - expects multipart/form-data
- GET `/invoice/{id}` - returns invoice details
- GET `/history` - returns all invoices
- DELETE `/invoice/{id}` - deletes invoice

Expected JSON format for invoice data.

### With Member 3 (DevOps):

Share these for deployment:
1. Run `npm run build`
2. Deploy `dist/` folder to Vercel
3. Set environment variable: `VITE_API_URL=<backend-url>`
4. Ensure backend CORS allows frontend domain

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

---

## Troubleshooting

**Port already in use:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
# Or change port
npm run dev -- --port 3000
```

**Dependencies issue:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
# Clear cache
rm -rf dist
npm run build
```

---

## Next Steps

1. ✅ Setup complete
2. ✅ All files created
3. ✅ Ready for development
4. ⏳ Wait for Member 2's backend
5. ⏳ Member 3 will handle deployment

---

## Your Responsibilities (Member 1)

✅ **Completed:**
- All UI components
- All pages
- API integration
- Responsive design
- Error handling
- Documentation

🚫 **NOT Your Responsibility:**
- Backend development
- OCR processing
- Database setup
- Cloud deployment
- Server configuration

---

**You're all set! Start the dev server and explore your frontend.**
