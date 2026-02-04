# Backend Deployment Guide

This guide covers deploying the FastAPI backend to Railway, Render, or Fly.io.

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

Railway is the easiest option with great WebSocket support.

#### Steps:

1. **Sign up at [railway.app](https://railway.app)**

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `RiteshRagav/SifyIntern_Work`

3. **Configure Service**
   - Railway will auto-detect the `railway.json` configuration
   - Set **Root Directory** to: `ai-preact-poc/backend`
   - Railway will use the Dockerfile automatically

4. **Add Environment Variables**
   Go to Variables tab and add:
   ```
   OPENAI_API_KEY=your_actual_key_here
   OPENAI_BASE_URL=https://infinitai.sifymdp.digital/maas/v1
   OPENAI_MODEL=gpt-4-turbo-preview
   MONGODB_URI=your_mongodb_connection_string
   MONGODB_DATABASE=storyboard_db
   CHROMADB_PERSIST_DIR=/tmp/chroma_data
   PORT=8000
   PYTHONUNBUFFERED=1
   ```

5. **Deploy**
   - Railway will automatically build and deploy
   - Wait for deployment to complete
   - Copy the generated URL (e.g., `https://your-app.railway.app`)

6. **Update Frontend**
   - Update Vercel environment variables:
     - `VITE_API_URL=https://your-app.railway.app`
     - `VITE_WS_URL=wss://your-app.railway.app`

---

### Option 2: Render

Render provides free tier with good WebSocket support.

#### Steps:

1. **Sign up at [render.com](https://render.com)**

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select: `RiteshRagav/SifyIntern_Work`

3. **Configure Service**
   - **Name**: `ai-preact-backend`
   - **Region**: Choose closest to you
   - **Branch**: `master` (or your main branch)
   - **Root Directory**: `ai-preact-poc/backend`
   - **Runtime**: Docker
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: `backend`

   OR use the `render.yaml` file:
   - Render will auto-detect `render.yaml` in root
   - It will configure everything automatically

4. **Add Environment Variables**
   In the Environment tab:
   ```
   OPENAI_API_KEY=your_actual_key_here
   OPENAI_BASE_URL=https://infinitai.sifymdp.digital/maas/v1
   OPENAI_MODEL=gpt-4-turbo-preview
   MONGODB_URI=your_mongodb_connection_string
   MONGODB_DATABASE=storyboard_db
   CHROMADB_PERSIST_DIR=/tmp/chroma_data
   PORT=8000
   PYTHONUNBUFFERED=1
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy
   - Copy the URL (e.g., `https://ai-preact-backend.onrender.com`)

6. **Update Frontend**
   - Update Vercel environment variables:
     - `VITE_API_URL=https://ai-preact-backend.onrender.com`
     - `VITE_WS_URL=wss://ai-preact-backend.onrender.com`

---

### Option 3: Fly.io

Fly.io offers global edge deployment.

#### Steps:

1. **Install flyctl**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Initialize**
   ```bash
   cd ai-preact-poc/backend
   fly launch
   ```
   - Choose app name
   - Select region
   - Don't deploy yet

4. **Configure**
   Edit `fly.toml` (auto-generated):
   ```toml
   [build]
     dockerfile = "Dockerfile"
   
   [env]
     PORT = "8000"
     PYTHONUNBUFFERED = "1"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http", "tls"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

5. **Set Secrets**
   ```bash
   fly secrets set OPENAI_API_KEY=your_key
   fly secrets set OPENAI_BASE_URL=https://infinitai.sifymdp.digital/maas/v1
   fly secrets set MONGODB_URI=your_mongodb_uri
   fly secrets set MONGODB_DATABASE=storyboard_db
   fly secrets set CHROMADB_PERSIST_DIR=/tmp/chroma_data
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

7. **Get URL**
   ```bash
   fly info
   ```
   Copy the URL and update frontend environment variables.

---

## 📋 Required Environment Variables

All platforms need these variables:

### Required:
- `OPENAI_API_KEY` - Your OpenAI API key
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DATABASE` - Database name (default: `storyboard_db`)

### Optional (with defaults):
- `OPENAI_BASE_URL` - Default: `https://infinitai.sifymdp.digital/maas/v1`
- `OPENAI_MODEL` - Default: `gpt-4-turbo-preview`
- `CHROMADB_PERSIST_DIR` - Default: `/tmp/chroma_data` (use `/tmp` for ephemeral storage)
- `PORT` - Default: `8000` (set automatically by platform)
- `PYTHONUNBUFFERED` - Set to `1` for better logging

## 🗄️ MongoDB Setup

You need a MongoDB instance. Options:

### Option 1: MongoDB Atlas (Free Tier)
1. Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Get connection string
4. Use as `MONGODB_URI`

### Option 2: Railway MongoDB
1. In Railway dashboard, click "New"
2. Select "Database" → "MongoDB"
3. Railway provides connection string automatically

### Option 3: Render MongoDB
1. In Render dashboard, click "New +"
2. Select "MongoDB"
3. Render provides connection string automatically

## ✅ Verification

After deployment, verify:

1. **Health Check**
   ```bash
   curl https://your-backend-url/health
   ```
   Should return: `{"status":"healthy",...}`

2. **API Root**
   ```bash
   curl https://your-backend-url/
   ```
   Should return API info

3. **Domains Endpoint**
   ```bash
   curl https://your-backend-url/api/domains
   ```
   Should return list of domains

4. **WebSocket** (if supported)
   - Test WebSocket connection in browser console or Postman
   - Connect to: `wss://your-backend-url/ws/test-session`

## 🔧 Troubleshooting

### Build Fails
- Check Dockerfile path is correct
- Verify Python version (3.11)
- Check requirements.txt exists

### App Crashes on Start
- Check environment variables are set
- Verify MongoDB connection string is correct
- Check logs in platform dashboard

### WebSocket Not Working
- Railway: WebSockets work automatically
- Render: Enable WebSocket support in settings
- Fly.io: WebSockets work automatically

### Port Issues
- Railway/Render: Use `$PORT` environment variable
- Fly.io: Configured in `fly.toml`

### ChromaDB Storage
- Use `/tmp/chroma_data` for ephemeral storage (data lost on restart)
- For persistent storage, use platform volumes (Railway/Render)

## 📚 Next Steps

After backend is deployed:

1. Copy backend URL
2. Update Vercel frontend environment variables
3. Test full application
4. Monitor logs for any issues

## 🆘 Support

- Railway: [docs.railway.app](https://docs.railway.app)
- Render: [render.com/docs](https://render.com/docs)
- Fly.io: [fly.io/docs](https://fly.io/docs)

