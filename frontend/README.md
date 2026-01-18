# Mnemonic Frontend

Next.js web interface for claim verification.

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install

# Copy environment file
cp .env.example .env.local

# Configure backend URL
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
pnpm dev
```

## 📦 Build for Production

```bash
pnpm build
pnpm start
```

## 🌐 Deploy to Vercel

### Option 1: Vercel CLI
```bash
npm i -g vercel
vercel
```

### Option 2: Vercel Dashboard
1. Import repository
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your backend URL
4. Deploy

### Environment Variables
```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

## 📚 Documentation

- [Main README](../README.md)
- [Split Deployment Guide](../SPLIT_DEPLOYMENT.md)
- [Architecture](../ARCHITECTURE.md)

## 🔧 Tech Stack

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Shadcn/UI
