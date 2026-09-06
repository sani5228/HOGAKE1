# HOGAKE Deployment Guide

## Quick Deployment to Render (Recommended)

### Prerequisites
- GitHub account (already have it ✓)
- Render account (free: https://render.com)

### Step-by-Step Deployment

#### 1. **Create Render Account**
   - Go to https://render.com
   - Sign in with GitHub
   - Authorize Render to access your repositories

#### 2. **Create PostgreSQL Database**
   - In Render dashboard, click **New +** → **PostgreSQL**
   - Set:
     - **Name:** `hogake-db`
     - **Database:** `procurement_db`
     - **User:** `postgres`
     - **Region:** Your preferred region
     - **Plan:** Free tier
   - Click **Create Database**
   - Copy the **Internal Database URL** (you'll need this)

#### 3. **Create Web Service**
   - Click **New +** → **Web Service**
   - Connect your GitHub repository: `sani5228/HOGAKE`
   - Set configuration:
     - **Name:** `hogake` (or `hogake-app`)
     - **Environment:** `Python 3`
     - **Region:** Same as database
     - **Branch:** `main`
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `gunicorn -b 0.0.0.0:$PORT 'backend.app:create_app()'`
     - **Plan:** Free tier

#### 4. **Add Environment Variables**
   In the Web Service settings, add these under **Environment**:
   ```
   FLASK_ENV=production
   DATABASE_URL=<paste your PostgreSQL Internal URL from step 2>
   JWT_SECRET=sih2026-hogake-production-secret-key-change-this
   CORS_ORIGINS=https://hogake.onrender.com
   CURRENT_SEASON=Kharif
   ```

#### 5. **Deploy**
   - Click **Create Web Service**
   - Render will automatically:
     - Pull your code from GitHub
     - Install Python dependencies
     - Build and deploy your app
     - Provide you with a live URL (e.g., `https://hogake.onrender.com`)

#### 6. **Initialize Database (One-Time)**
   After deployment succeeds:
   ```bash
   # SSH into your Render service or run from your local machine:
   curl https://hogake.onrender.com/api/health
   
   # If you need to seed the database:
   # You may need to create a deployment task in Render
   ```

---

## Alternative Deployment Options

### **Option A: DigitalOcean App Platform**
1. Go to https://cloud.digitalocean.com/apps
2. Connect GitHub repository
3. Select `sani5228/HOGAKE`
4. Set build command: `pip install -r backend/requirements.txt`
5. Set run command: `gunicorn -b 0.0.0.0:$PORT 'backend.app:create_app()'`
6. Add PostgreSQL database
7. Deploy (~$5-12/month)

### **Option B: Azure App Service**
1. Go to https://portal.azure.com
2. Create **App Service** (Python 3.11)
3. Connect GitHub repository
4. Configure deployment slots
5. Add PostgreSQL instance
6. Deploy (~$10-20/month)

### **Option C: Railway (Simplest)**
1. Go to https://railway.app
2. Click **New Project** → **Deploy from GitHub**
3. Select `sani5228/HOGAKE`
4. Add PostgreSQL plugin
5. Set environment variables
6. Deploy (~$5/month after free credits)

---

## Post-Deployment Checklist

- [ ] App is running at the provided URL
- [ ] Database connection is working
- [ ] Frontend loads at root URL (`/`)
- [ ] API endpoints respond (`/api/health`, `/api/auth/login`)
- [ ] Farmer login works
- [ ] Admin login works
- [ ] Center login works

---

## Environment Variables Reference

| Variable | Production Value | Notes |
|----------|------------------|-------|
| `FLASK_ENV` | `production` | Production mode enabled |
| `DATABASE_URL` | PostgreSQL connection | Render provides this automatically |
| `JWT_SECRET` | Generate a strong secret | Used for authentication tokens |
| `CORS_ORIGINS` | Your domain URL | e.g., `https://hogake.onrender.com` |
| `CURRENT_SEASON` | `Kharif` or `Rabi` | Agricultural season |

---

## Monitoring & Support

### Logs
- **Render:** Dashboard → Web Service → Logs
- Check for errors during deployment

### Common Issues

**1. Database Connection Error**
```
Error: could not translate host name "..."
```
✓ Solution: Ensure DATABASE_URL is correct internal connection string

**2. Port Binding Error**
```
Error: Address already in use
```
✓ Solution: Flask is hardcoded to use $PORT environment variable

**3. Module Not Found**
```
ModuleNotFoundError: No module named 'backend'
```
✓ Solution: Ensure `backend/requirements.txt` includes `gunicorn`

---

## Next Steps

1. **Test all user flows:**
   - Farmer registration → Login → Slot booking
   - Center staff login → Manage bookings
   - Admin login → System configuration

2. **Set up monitoring:**
   - Enable error tracking (Sentry, DataDog)
   - Set up uptime monitoring

3. **Configure domain:**
   - Add custom domain to Render (optional)
   - Update `CORS_ORIGINS` if using custom domain

4. **Security hardening:**
   - Change default JWT_SECRET
   - Enable HTTPS (automatic on Render)
   - Review database backups

---

## Rollback

If deployment fails:
1. Check logs in Render dashboard
2. Fix the issue in your repository
3. Push to GitHub
4. Render will auto-redeploy on push

---

**Need help?** Check Render docs: https://render.com/docs
