# Quick Start: Deploy to Vercel

## 🚀 Fastest Way to Deploy

### 1. Connect to Vercel (2 minutes)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click "Import Git Repository"
3. Select `RiteshRagav/SifyIntern_Work`
4. Configure:
   - **Root Directory**: `ai-preact-poc/frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

### 2. Set Environment Variables

In Vercel dashboard → Settings → Environment Variables, add:

```
VITE_API_URL=https://your-backend-url.railway.app
VITE_WS_URL=wss://your-backend-url.railway.app
```

**Note**: Replace with your actual backend URL after deploying backend.

### 3. Deploy Backend (Choose One)

#### Railway (Easiest)
```bash
# 1. Go to railway.app → New Project → Deploy from GitHub
# 2. Select repository → Set root to: ai-preact-poc/backend
# 3. Add environment variables (see VERCEL_DEPLOYMENT.md)
# 4. Deploy!
```

#### Render
```bash
# 1. Go to render.com → New Web Service
# 2. Connect GitHub → Select repo
# 3. Settings:
#    - Build: pip install -r requirements.txt
#    - Start: uvicorn main:app --host 0.0.0.0 --port $PORT
# 4. Add env vars → Deploy
```

### 4. Update Frontend URL

After backend deploys:
1. Copy backend URL
2. Update Vercel env vars:
   - `VITE_API_URL` = `https://your-backend-url`
   - `VITE_WS_URL` = `wss://your-backend-url`
3. Redeploy frontend (or wait for auto-deploy)

## ✅ Done!

Your app should now be live at: `https://your-project.vercel.app`

## 🔧 Troubleshooting

**Build fails?**
- Check Node.js version (needs 18+)
- Verify `frontend/package.json` exists
- Check build logs in Vercel

**Frontend can't connect to backend?**
- Verify `VITE_API_URL` is set correctly
- Check backend is running
- Test backend URL directly: `curl https://your-backend-url/api/domains`

**WebSocket not working?**
- Vercel doesn't support WebSockets
- Deploy backend to Railway/Render/Fly.io
- Or use SSE endpoints (modify frontend code)

## 📚 Full Documentation

See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for detailed instructions.

