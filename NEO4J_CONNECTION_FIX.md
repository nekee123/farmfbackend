# Neo4j Connection Error - Fix Guide

## 🔴 Current Error

```
neo4j.exceptions.ServiceUnavailable: Failed to read from defunct connection 
IPv4Address(('f16c6d3b.databases.neo4j.io', 7687))
```

Your backend cannot connect to the Neo4j Aura database, which is why the frontend shows errors when loading data.

## ✅ Solution Steps

### Step 1: Check Neo4j Aura Database Status

1. **Go to Neo4j Aura Console:**
   - Visit: https://console.neo4j.io/
   - Log in with your credentials

2. **Check Database Status:**
   - Look for your database instance
   - Status should be **"Running"** (green)
   - If it shows **"Paused"** or **"Stopped"**, click **Resume**

3. **Free Tier Note:**
   - Neo4j Aura free tier pauses after 3 days of inactivity
   - You need to manually resume it

### Step 2: Get Correct Connection Details

From your Neo4j Aura dashboard:

1. Click on your database instance
2. Click **"Connect"** button
3. Copy these values:

```
Connection URI: neo4j+s://f16c6d3b.databases.neo4j.io
Username: neo4j (usually)
Password: [your password from when you created the database]
```

**Important:** The URI should start with `neo4j+s://` (with the `+s` for secure connection)

### Step 3: Update Render Environment Variables

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com/
   - Select your backend service: `isdamarket-3`

2. **Go to Environment Tab:**
   - Click on **"Environment"** in the left sidebar

3. **Add/Update these variables:**

```
NEO4J_URI=neo4j+s://f16c6d3b.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_actual_password_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

4. **Save Changes:**
   - Click **"Save Changes"**
   - Render will automatically redeploy your service

### Step 4: Verify IP Whitelist in Neo4j Aura

1. In Neo4j Aura dashboard, go to your database
2. Click on **"Connection"** or **"Network Access"** tab
3. Check **IP Allowlist**:
   - Should show `0.0.0.0/0` (allows all IPs)
   - If not, click **"Edit"** and add `0.0.0.0/0`

### Step 5: Test Connection Locally

Before redeploying, test the connection locally:

1. **Update your local `.env` file:**
   ```bash
   # In: C:\Users\chuan\OneDrive\Documents\IsdaMarket\.env
   NEO4J_URI=neo4j+s://f16c6d3b.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   JWT_SECRET_KEY=your_secret_key
   ```

2. **Run backend locally:**
   ```bash
   cd C:\Users\chuan\OneDrive\Documents\IsdaMarket
   python run.py
   ```

3. **Test endpoints:**
   - Open: http://localhost:8000/docs
   - Try: GET /products/
   - Should return data (not error)

### Step 6: Verify Render Deployment

After updating environment variables on Render:

1. **Check Render Logs:**
   - In Render dashboard → Your service → Logs
   - Look for: `✓ Connected to Neo4j database`
   - Should NOT see: `ServiceUnavailable` errors

2. **Test Backend:**
   - Open: https://isdamarket-3.onrender.com/docs
   - Try: GET /products/
   - Should return JSON data

3. **Test Frontend:**
   - Rebuild frontend: `npm run build`
   - Deploy and test Browse Fish page

## 🔍 Common Issues & Solutions

### Issue 1: "Database is Paused"
**Solution:** Resume the database in Neo4j Aura console

### Issue 2: "Authentication failed"
**Solution:** 
- Reset password in Neo4j Aura
- Update NEO4J_PASSWORD in Render environment variables

### Issue 3: "Connection timeout"
**Solution:**
- Check IP whitelist includes `0.0.0.0/0`
- Verify database is running (not paused)

### Issue 4: "Wrong URI format"
**Solution:**
- URI should be: `neo4j+s://xxxxx.databases.neo4j.io`
- NOT: `bolt://` or `neo4j://` (without +s)

## 📋 Checklist

- [ ] Neo4j Aura database is **Running** (not paused)
- [ ] Connection URI copied from Neo4j Aura (starts with `neo4j+s://`)
- [ ] Username is correct (usually `neo4j`)
- [ ] Password is correct
- [ ] IP whitelist includes `0.0.0.0/0`
- [ ] Render environment variables updated
- [ ] Render service redeployed
- [ ] Backend logs show successful connection
- [ ] Test endpoint returns data

## 🚀 Quick Test Commands

**Test Neo4j connection from Python:**
```python
from neo4j import GraphDatabase

uri = "neo4j+s://f16c6d3b.databases.neo4j.io"
driver = GraphDatabase.driver(uri, auth=("neo4j", "your_password"))

with driver.session() as session:
    result = session.run("RETURN 1 as num")
    print(result.single()["num"])  # Should print: 1

driver.close()
```

**Test backend endpoint:**
```bash
curl https://isdamarket-3.onrender.com/products/
```

## 📞 Need Help?

If the issue persists:
1. Check Neo4j Aura status page
2. Verify all credentials are correct
3. Check Render logs for specific error messages
4. Ensure database hasn't been deleted
