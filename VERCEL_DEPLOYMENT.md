# Vercel Deployment Guide

This guide will help you deploy the AI Preact POC application to Vercel.

## ⚠️ Important Notes

**WebSocket Limitation**: Vercel serverless functions do not support WebSocket connections. The backend uses WebSockets for real-time agent streaming. For full functionality, you have two options:

1. **Deploy frontend to Vercel + Backend separately** (Recommended)
   - Frontend: Vercel (this guide)
   - Backend: Railway, Render, Fly.io, or similar (supports WebSockets)

2. **Use SSE (Server-Sent Events) instead of WebSockets**
   - The backend already supports SSE endpoints
   - Update frontend to use SSE instead of WebSocket

## Prerequisites

- Vercel account (sign up at [vercel.com](https://vercel.com))
- GitHub account (code is already pushed to GitHub)
- Node.js 18+ installed locally (for testing)

## Step 1: Deploy Frontend to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository: `RiteshRagav/SifyIntern_Work`
   - Vercel will auto-detect the configuration

2. **Configure Project Settings**
   - **Framework Preset**: Vite
   - **Root Directory**: `ai-preact-poc/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Environment Variables**
   Add these in Vercel dashboard under Settings → Environment Variables:
   ```
   VITE_API_URL=https://your-backend-url.com
   VITE_WS_URL=wss://your-backend-url.com
   ```
   Replace `your-backend-url.com` with your actual backend URL.

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your frontend will be live!

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project root
cd ai-preact-poc

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? ai-preact-poc (or your choice)
# - Directory? frontend
# - Override settings? No

# Set environment variables
vercel env add VITE_API_URL
vercel env add VITE_WS_URL

# Deploy to production
vercel --prod
```

## Step 2: Deploy Backend (Separate Service)

Since Vercel doesn't support WebSockets, deploy the backend separately:

### Option 1: Railway (Recommended for WebSockets)

1. Go to [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Select your repository
4. Set root directory to `ai-preact-poc/backend`
5. Add environment variables:
   ```
   OPENAI_API_KEY=your_key
   OPENAI_BASE_URL=https://infinitai.sifymdp.digital/maas/v1
   MONGODB_URI=your_mongodb_uri
   MONGODB_DATABASE=storyboard_db
   CHROMADB_PERSIST_DIR=/tmp/chroma_data
   ```
6. Railway will auto-detect Python and install dependencies
7. Update frontend `VITE_API_URL` to Railway URL

### Option 2: Render

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add environment variables (same as Railway)
6. Deploy

### Option 3: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Initialize (in backend directory)
cd ai-preact-poc/backend
fly launch

# Set secrets
fly secrets set OPENAI_API_KEY=your_key
fly secrets set MONGODB_URI=your_uri
# ... etc

# Deploy
fly deploy
```

## Step 3: Update Frontend Environment Variables

After backend is deployed, update Vercel environment variables:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update:
   ```
   VITE_API_URL=https://your-backend.railway.app (or render/fly URL)
   VITE_WS_URL=wss://your-backend.railway.app (or render/fly URL)
   ```
3. Redeploy frontend (or wait for auto-deploy)

## Step 4: Test Deployment

1. Visit your Vercel frontend URL
2. Test normal chat mode (should work)
3. Test multi-agent mode (requires WebSocket backend)

## Troubleshooting

### Frontend shows "Connection Error"
- Check `VITE_API_URL` is set correctly in Vercel
- Verify backend is running and accessible
- Check CORS settings in backend

### WebSocket Connection Fails
- Vercel doesn't support WebSockets
- Deploy backend to Railway/Render/Fly.io
- Or use SSE endpoints instead (modify frontend)

### Build Fails
- Check Node.js version (needs 18+)
- Verify all dependencies in `package.json`
- Check build logs in Vercel dashboard

### Environment Variables Not Working
- Variables must start with `VITE_` to be exposed to frontend
- Redeploy after adding variables
- Check variable names match exactly

## Alternative: Use SSE Instead of WebSocket

If you want everything on Vercel, modify the frontend to use SSE:

1. Backend already has SSE endpoint: `/api/events/{session_id}`
2. Update `frontend/src/utils/wsClient.js` to use EventSource instead of WebSocket
3. This will work with Vercel serverless functions

## Project Structure

```
ai-preact-poc/
├── frontend/          # React/Vite frontend (deploy to Vercel)
├── backend/           # FastAPI backend (deploy separately)
├── vercel.json        # Vercel configuration
└── package.json       # Root package.json for Vercel
```

## Environment Variables Reference

### Frontend (Vercel)
- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - Backend WebSocket URL

### Backend (Railway/Render/Fly.io)
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_BASE_URL` - OpenAI base URL
- `OPENAI_MODEL` - Model name (default: gpt-4-turbo-preview)
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DATABASE` - Database name
- `CHROMADB_PERSIST_DIR` - ChromaDB storage path
- `DEBUG` - Debug mode (true/false)

## Support

For issues:
1. Check Vercel build logs
2. Check backend logs (Railway/Render/Fly.io)
3. Verify environment variables are set correctly
4. Test backend endpoints directly (curl/Postman)

