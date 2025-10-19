# IsdaMarket Backend - Deployment Checklist

## Current Configuration

**Backend Location:** `C:\Users\chuan\OneDrive\Documents\IsdaMarket`
**Frontend Location:** `C:\Users\chuan\isdamarket-frontend`
**Deployed Backend URL:** `https://isdamarket-3.onrender.com`

## ✅ Backend Status

Your backend is properly configured with:
- ✅ FastAPI application (`app/main.py`)
- ✅ Procfile for Render deployment
- ✅ CORS enabled for all origins
- ✅ Neo4j Aura database connection
- ✅ All routes included (sellers, buyers, products, orders, messages, reviews, notifications)

## 🔍 Deployment Verification Steps

### 1. Check Render Dashboard
Go to your Render dashboard and verify:
- [ ] Service is **Live** (not sleeping/failed)
- [ ] Service name matches: `isdamarket-3`
- [ ] Latest deployment succeeded
- [ ] Environment variables are set:
  - `NEO4J_URI`
  - `NEO4J_USER`
  - `NEO4J_PASSWORD`

### 2. Test Backend Endpoints

Open these URLs in your browser to verify the backend is working:

**API Documentation:**
```
https://isdamarket-3.onrender.com/docs
```

**Root Endpoint (should redirect to /docs):**
```
https://isdamarket-3.onrender.com/
```

**Test Products Endpoint:**
```
https://isdamarket-3.onrender.com/products/
```

**Health Check (if available):**
```
https://isdamarket-3.onrender.com/health
```

### 3. Common Issues & Solutions

#### Issue: Backend is sleeping (503 error or timeout)
**Solution:** 
- Free tier Render services sleep after 15 minutes of inactivity
- First request takes 30-60 seconds to wake up
- Wait and refresh, or upgrade to paid tier for always-on service

#### Issue: CORS errors in browser console
**Solution:**
- Your backend already has CORS enabled for all origins (line 34 in main.py)
- If still seeing errors, check browser console for specific error message

#### Issue: Database connection errors
**Solution:**
- Verify Neo4j Aura credentials in Render environment variables
- Check Neo4j Aura instance is running
- Verify IP whitelist includes Render's IPs (or set to 0.0.0.0/0)

#### Issue: Wrong backend URL
**Solution:**
If the URL is different, update frontend `.env.production`:
```bash
# In: C:\Users\chuan\isdamarket-frontend\.env.production
REACT_APP_API_URL=https://your-actual-url.onrender.com
```

## 🚀 Frontend Deployment

Your frontend is already configured to use the backend:
- ✅ `.env.production` points to `https://isdamarket-3.onrender.com`
- ✅ Centralized API configuration in `src/config/api.js`
- ✅ Error boundary to prevent white screens
- ✅ All pages updated to use centralized BASE_URL

### To Deploy Frontend:

1. **Build the app:**
   ```bash
   cd C:\Users\chuan\isdamarket-frontend
   npm run build
   ```

2. **Deploy to hosting service** (Netlify, Vercel, etc.)
   - Upload the `build` folder
   - No additional environment variables needed (uses `.env.production`)

## 🧪 Testing After Deployment

1. **Test backend directly:**
   - Visit `https://isdamarket-3.onrender.com/docs`
   - Try a GET request to `/products/`
   - Verify response is JSON (not error)

2. **Test frontend:**
   - Navigate to Browse Fish page
   - Navigate to My Orders page
   - Navigate to Account Settings page
   - Check browser console for errors

3. **Test integration:**
   - Try logging in as buyer
   - Browse products
   - Place an order
   - Check if data appears

## 📝 Next Steps

1. [ ] Verify backend is running on Render
2. [ ] Test backend endpoints directly
3. [ ] Rebuild frontend with `npm run build`
4. [ ] Deploy frontend
5. [ ] Test all pages (Browse Fish, My Orders, Settings)

## 🔗 Important URLs

**Backend:**
- Production: `https://isdamarket-3.onrender.com`
- Docs: `https://isdamarket-3.onrender.com/docs`

**Frontend:**
- Development: `http://localhost:3000`
- Production: (Your hosting URL)

## 💡 Tips

- **First load is slow:** Render free tier services sleep. First request takes time.
- **Check logs:** In Render dashboard, check "Logs" tab for errors
- **Database issues:** Verify Neo4j Aura is running and accessible
- **CORS issues:** Already configured, but check browser console for specifics
