# FXTrade Setup Guide

## How Contributing Works

### Development → Deployment Flow

```
1. Code Locally              2. Push to GitHub         3. Auto-Deploy
   ↓                            ↓                         ↓
[Your Computer]     →    [GitHub Repository]    →    [Google Cloud]
Docker Compose           GitHub Actions              Cloud Run
localhost:5173           Build & Test                Live Production
                         Deploy if tests pass
```

### Step-by-Step Process

**1. Work on a Feature**
```bash
# Make changes to the code
# Test locally with Docker
docker-compose up

# Visit http://localhost:5173 to test your changes
```

**2. Commit Your Changes**
```bash
git add .
git commit -m "Add new feature"
git push origin main
```

**3. Automatic Deployment** (GitHub Actions takes over)

Once you push, GitHub Actions automatically:

```
✓ Runs tests (CI workflow)
  - Lints Python code
  - Builds frontend to check for errors

✓ Builds Docker images
  - Backend: Python app + dependencies
  - Frontend: Vue app compiled + Nginx

✓ Pushes to Artifact Registry
  - Stores Docker images in GCP

✓ Deploys to Cloud Run
  - Starts new containers with your code
  - Routes traffic to new version
  - Old version kept for rollback

✓ Live in ~2-5 minutes
```

**4. Check Deployment**

- **Monitor:** GitHub → Actions tab (see real-time logs)
- **Visit:** Your live site URL (e.g., `https://fxtrade-frontend-xxx.run.app`)
- **Verify:** Backend API at `https://fxtrade-backend-xxx.run.app`

### What Triggers Deployment?

| File Changed | What Deploys |
|--------------|-------------|
| `backend/**/*.py` | Backend only |
| `frontend/**/*.vue`, `frontend/**/*.js` | Frontend only |
| Both | Both deploy in parallel |
| `README.md`, docs | Nothing (no deploy needed) |

### Example Contribution

```bash
# 1. Fix a bug in login page
code frontend/src/views/LoginView.vue

# 2. Test locally
docker-compose up
# Test at localhost:5173

# 3. Commit and push
git add frontend/src/views/LoginView.vue
git commit -m "Fix: Email validation on login"
git push origin main

# 4. Watch it deploy
# → Go to GitHub.com/your-repo/actions
# → See "Deploy Frontend to Cloud Run" running
# → Wait 2-3 minutes
# → Live on production! ✓
```

### Team Workflow

**For multiple contributors:**

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   # Make changes
   git push origin feature/my-feature
   ```

2. **Create Pull Request on GitHub**
   - CI tests run automatically
   - Team reviews code
   - Merge when approved

3. **Merge to main** → Auto-deploys!

### Safety Features

- ✅ **Tests run first** - Won't deploy if tests fail
- ✅ **Rollback available** - Can revert to previous version in GCP Console
- ✅ **Separate workflows** - Frontend and backend deploy independently
- ✅ **Environment variables** - Secrets stored securely in GitHub

## Quick Start

### 1. Setup

```bash
./setup.sh
```

Or manually:
```bash
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install
```

### 2. Configure Supabase

Edit `backend/.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Get from: https://app.supabase.com → Settings → API

### 3. Run

**With Docker:**
```bash
docker-compose up
```

**Without Docker:**
```bash
# Terminal 1
cd backend && source venv/bin/activate && python main.py

# Terminal 2
cd frontend && npm run dev
```

**URLs:**
- Frontend: http://localhost:5173 (or localhost:3000 with Docker)
- Backend: http://localhost:8000

## Deploy to GCP

### One-Time Setup

```bash
# Login and create project
gcloud auth login
gcloud projects create my-fxtrade --set-as-default

# Enable required services
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create Docker registry
gcloud artifacts repositories create fxtrade-repo \
  --repository-format=docker \
  --location=us-central1
```

### Manual Deploy

```bash
# Backend
cd backend
gcloud run deploy fxtrade-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key

# Frontend (use backend URL from above)
cd frontend
echo "VITE_API_URL=https://fxtrade-backend-xxx.run.app" > .env.production
gcloud run deploy fxtrade-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Update CORS

Add your frontend URL to `backend/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "https://fxtrade-frontend-xxx.run.app"
]
```

Redeploy backend.

## Auto-Deploy with GitHub Actions

Pushes to `main` branch auto-deploy!

### Setup Instructions

**1. Create Service Account**

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com
```

**2. Add GitHub Secrets**

Go to: GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | How to Get |
|------------|-------|------------|
| `GCP_PROJECT_ID` | Your GCP project ID | From GCP Console |
| `GCP_SA_KEY` | Service account JSON key | Content of `key.json` file |
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase anon key | Supabase Dashboard → Settings → API |
| `BACKEND_URL` | Backend URL | After first deploy: `https://fxtrade-backend-xxx.run.app` |

**Important:** Delete `key.json` after adding to GitHub!
```bash
rm key.json
```

**3. First Deploy**

Deploy backend manually once to get the URL:
```bash
cd backend
gcloud run deploy fxtrade-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=your_url,SUPABASE_KEY=your_key
```

Add the backend URL to GitHub secrets as `BACKEND_URL`.

**4. Test Auto-Deploy**

```bash
git add .
git commit -m "Test auto-deploy"
git push origin main
```

Check GitHub → Actions tab to see deployment progress.

### How It Works

1. Push code to `main` branch
2. GitHub Actions triggers (see `.github/workflows/`)
3. Builds Docker image with your code
4. Pushes to Artifact Registry
5. Deploys to Cloud Run
6. Live in ~2-5 minutes

**Workflows:**
- `ci.yml` - Runs tests on every push/PR
- `deploy-backend.yml` - Deploys backend when backend code changes
- `deploy-frontend.yml` - Deploys frontend when frontend code changes

## Troubleshooting

**Backend won't start:**
- Check `.env` exists with Supabase credentials
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**Frontend won't start:**
- Run `npm install`
- Need Node 18+: `node --version`

**Deployment fails:**
- Verify all GitHub secrets are set correctly
- Check service account has required permissions
- View logs in GitHub Actions tab

**CORS errors in production:**
- Update `allow_origins` in `backend/main.py`
- Redeploy backend

**Artifact Registry push fails:**
- Verify repository exists: `gcloud artifacts repositories list`
- Check service account has `artifactregistry.admin` role

## Monitoring

- **View deployment logs:** GitHub repo → Actions tab
- **View running services:** GCP Console → Cloud Run
- **Rollback if needed:** Cloud Run console → Select previous revision
