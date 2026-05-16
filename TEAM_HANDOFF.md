# Team Handoff Guide

## What to Share with Each Team Member

---

## 📤 For Member 2 (Backend + AI/OCR Engineer)

### Priority Documents

1. **API_CONTRACT.md** ⭐ MOST IMPORTANT
   - Contains exact API specifications
   - Request/response formats
   - Data models
   - Error handling requirements
   - CORS requirements

2. **README.md** (API Integration section)
   - Overview of what frontend expects
   - JSON response format examples

### Key Information to Communicate

**Required Endpoints:**
```
POST   /upload          - Upload and process invoices
GET    /invoice/{id}    - Get specific invoice details
GET    /history         - List all processed invoices
DELETE /invoice/{id}    - Delete invoice
```

**Expected JSON Format:**
```json
{
  "document_id": "DOC101",
  "invoice_count": 1,
  "validation_status": "valid",
  "is_valid": true,
  "validation_errors": [],
  "confidence_score": 95.5,
  "invoices": [{
    "invoice_number": "INV-001",
    "seller_name": "ABC Ltd",
    "buyer_name": "XYZ Ltd",
    "total_amount": 1200.00,
    "line_items": [...]
  }]
}
```

**CORS Configuration Required:**
```python
# FastAPI example
allow_origins=[
    "http://localhost:5173",  # Development
    "https://your-app.vercel.app"  # Production
]
```

### Testing Together

Once backend is ready:

1. **Start backend:** `uvicorn main:app --reload`
2. **Start frontend:** `npm run dev`
3. **Test endpoints:**
   - Upload a test invoice
   - Verify it appears in dashboard
   - Click to view details
   - Test delete functionality

### What Frontend Sends

**Upload Request:**
- Content-Type: `multipart/form-data`
- Field name: `file` or `files`
- Accepts: image/*, application/pdf

**Other Requests:**
- Standard HTTP GET/DELETE
- JSON responses expected

---

## 🚀 For Member 3 (Deployment + DevOps Engineer)

### Priority Documents

1. **README.md** (Deployment section)
   - Build commands
   - Output directory
   - Environment variables

2. **SETUP.md**
   - Quick reference for setup
   - Configuration details

### Deployment Instructions

#### Frontend Deployment (Vercel)

**Build Command:**
```bash
npm run build
```

**Output Directory:**
```
dist/
```

**Environment Variables:**
```
VITE_API_URL=https://your-backend.onrender.com
```

**Vercel Settings:**
```yaml
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Node Version: 18.x
```

**Root Directory:**
```
./
```

#### Steps to Deploy

1. **Connect GitHub Repository**
   - Link your GitHub repo to Vercel
   - Select the main branch

2. **Configure Build Settings**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Set Environment Variables**
   - Add `VITE_API_URL` in Vercel dashboard
   - Point it to Member 2's deployed backend URL

4. **Deploy**
   - Click deploy
   - Wait for build to complete
   - Verify the site loads

5. **Configure Domain (Optional)**
   - Add custom domain if needed
   - Update CORS on backend to allow this domain

#### Backend Integration

**What you need from Member 2:**
- Backend URL (e.g., `https://api.invoiceocr.onrender.com`)
- Confirmation that CORS is enabled for your frontend domain

**What Member 2 needs from you:**
- Frontend URL (e.g., `https://invoiceocr.vercel.app`)
- So they can add it to CORS allowed origins

#### MongoDB Setup (Your Responsibility)

While you handle database setup:
- Frontend doesn't directly connect to MongoDB
- All database operations go through backend API
- Just ensure Member 2 has the MongoDB connection string

#### Verification Checklist

After deployment:
- [ ] Frontend loads at Vercel URL
- [ ] Can navigate between pages
- [ ] Backend API URL is correct in env vars
- [ ] Upload triggers API call to backend
- [ ] Dashboard fetches from backend
- [ ] Details page works
- [ ] Delete functionality works
- [ ] No CORS errors in browser console

#### Troubleshooting Deployment

**Build Fails:**
```bash
# Locally test build
npm run build

# If it works locally, check:
- Node version on Vercel (should be 18.x)
- Environment variables are set
- Dependencies installed correctly
```

**CORS Errors:**
```
Backend must include frontend domain:
allow_origins=["https://your-app.vercel.app"]
```

**API Calls Fail:**
```
Verify VITE_API_URL is set correctly:
- Check Vercel environment variables
- Redeploy after changing env vars
- Verify backend is deployed and accessible
```

---

## 👥 Team Coordination

### Timeline

**Week 1-2:**
- Member 1 (You): ✅ Frontend complete
- Member 2: Developing backend + OCR
- Member 3: Setting up infrastructure

**Week 2-3:**
- Member 1: Testing with Member 2's backend
- Member 2: Finalizing API endpoints
- Member 3: Preparing deployment

**Week 3-4:**
- Member 1: Bug fixes and polish
- Member 2: Production-ready backend
- Member 3: Deploy both frontend and backend

**Week 4:**
- All: Integration testing
- All: Final demo preparation

### Communication Points

#### Member 1 ↔️ Member 2

**Initial:**
- Share API_CONTRACT.md
- Agree on JSON format
- Confirm endpoint URLs

**During Development:**
- Test endpoints as they're ready
- Report any data format issues
- Coordinate on error messages

**Before Deployment:**
- Final API testing
- Verify all features work
- Test error scenarios

#### Member 1 ↔️ Member 3

**Initial:**
- Share deployment requirements
- Provide build commands
- List environment variables

**During Deployment:**
- Provide any needed assistance
- Verify build succeeds
- Test deployed site

**After Deployment:**
- Confirm all features work
- Test on different devices
- Verify backend integration

#### Member 2 ↔️ Member 3

**Required:**
- Backend deployment URL
- Frontend deployment URL
- CORS configuration
- MongoDB connection string

---

## 📋 Integration Checklist

### Before Integration

- [x] Frontend built and tested locally (Member 1)
- [ ] Backend endpoints implemented (Member 2)
- [ ] Database setup complete (Member 3)
- [ ] CORS configured (Member 2)
- [ ] Environment variables ready (Member 3)

### During Integration

- [ ] Test upload endpoint
- [ ] Test get invoice endpoint
- [ ] Test history endpoint
- [ ] Test delete endpoint
- [ ] Verify error handling
- [ ] Test with real invoice images
- [ ] Check validation display
- [ ] Verify confidence scores

### After Integration

- [ ] All features work end-to-end
- [ ] Error messages are user-friendly
- [ ] Loading states appear correctly
- [ ] Data persists in database
- [ ] Can delete and re-upload
- [ ] Mobile responsive works
- [ ] No console errors

---

## 🐛 Common Issues & Solutions

### Issue: CORS Errors

**Symptom:** 
Browser console shows: "Access to fetch at 'http://backend' from origin 'http://frontend' has been blocked by CORS policy"

**Solution:**
Member 2 must add to backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: API Not Found (404)

**Symptom:**
Frontend shows "Backend not responding"

**Solutions:**
1. Verify backend is running
2. Check `VITE_API_URL` is correct
3. Verify endpoint paths match
4. Check backend logs

### Issue: Upload Fails

**Symptom:**
File upload shows error

**Check:**
1. Backend accepts multipart/form-data
2. Field name matches ('file' or 'files')
3. File size limits
4. File type validation

### Issue: Data Format Mismatch

**Symptom:**
Data doesn't display correctly

**Solution:**
1. Check API_CONTRACT.md
2. Verify JSON structure matches
3. Add console.log to see actual data
4. Adjust frontend or backend accordingly

---

## 📞 Contact Protocol

### For Technical Issues

**Frontend Issues:**
- Contact Member 1 (You)
- Check DEVELOPER_GUIDE.md
- Review browser console

**Backend Issues:**
- Contact Member 2
- Check backend logs
- Verify API responses

**Deployment Issues:**
- Contact Member 3
- Check build logs
- Verify environment variables

### For Integration Issues

**All Members:**
- Schedule a call/meeting
- Share screen to debug together
- Check network tab in browser
- Review logs from all systems

---

## 🎯 Success Metrics

### When You Know It's Working

1. **Upload Flow:**
   - Select file on frontend
   - Upload with progress bar
   - Backend processes it
   - Redirects to dashboard
   - Invoice appears in list

2. **View Flow:**
   - Click invoice card
   - Details page loads
   - All data displays correctly
   - Validation status shows
   - Line items appear

3. **Delete Flow:**
   - Click delete button
   - Confirmation dialog appears
   - Backend deletes from database
   - Frontend removes from list

4. **Search Flow:**
   - Type in search box
   - Results filter in real-time
   - Correct invoices show

---

## 📦 Handoff Package

### For Member 2

Send them:
```
Files:
- API_CONTRACT.md
- README.md (API Integration section)

Key Info:
- POST /upload endpoint requirements
- JSON response format
- CORS configuration needed
- Development URL: http://localhost:5173
```

### For Member 3

Send them:
```
Files:
- README.md (Deployment section)
- SETUP.md
- .env.example

Key Info:
- Build command: npm run build
- Output: dist/
- Env var: VITE_API_URL
- Node version: 18.x
```

---

## 🚀 Quick Start for Each Member

### Member 2 - To Start Backend Development

1. Read API_CONTRACT.md
2. Implement 4 endpoints
3. Enable CORS for http://localhost:5173
4. Test with curl or Postman
5. Return JSON in specified format
6. Notify Member 1 when ready to test

### Member 3 - To Start Deployment

1. Read README.md deployment section
2. Setup Vercel account
3. Setup Render account (for backend)
4. Setup MongoDB Atlas
5. Prepare to receive:
   - Frontend repo (this)
   - Backend repo (from Member 2)
6. Configure environment variables

---

## ✅ Final Handoff Checklist

### Member 1 → Member 2

- [ ] Shared API_CONTRACT.md
- [ ] Explained JSON format requirements
- [ ] Provided example requests/responses
- [ ] Listed required endpoints
- [ ] Specified CORS requirements
- [ ] Available for questions

### Member 1 → Member 3

- [ ] Shared deployment documentation
- [ ] Provided build commands
- [ ] Listed environment variables
- [ ] Explained output structure
- [ ] Available for deployment support

### Entire Team

- [ ] Communication channels established
- [ ] Timeline agreed upon
- [ ] Responsibilities clear
- [ ] Integration plan defined
- [ ] Testing strategy agreed
- [ ] Demo date set

---

**Remember: We're a team! Help each other succeed. 🤝**

---

## 📅 Suggested Meeting Schedule

### Week 1
**Initial Sync Meeting (30 min)**
- Discuss project overview
- Confirm responsibilities
- Share timelines
- Exchange contact info

### Week 2
**Progress Check-in (15 min)**
- Member 1: Frontend status ✅ (Complete)
- Member 2: Backend progress
- Member 3: Infrastructure status
- Address blockers

### Week 3
**Integration Planning (45 min)**
- Review API contract
- Test endpoints together
- Plan deployment
- Assign integration tasks

### Week 4
**Pre-deployment Testing (1 hour)**
- Test all features
- Fix bugs
- Verify data flow
- Prepare for deployment

**Deployment Session (2 hours)**
- Deploy backend (Member 3)
- Deploy frontend (Member 3)
- Configure environment
- Integration testing
- Bug fixes

### Final
**Demo Preparation (30 min)**
- Prepare presentation
- Test demo flow
- Prepare talking points
- Final polish

---

**This handoff guide ensures smooth collaboration between all team members!**

**Good luck with the integration! 🎉**
