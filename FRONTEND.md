# Frontend - Next.js + shadcn/ui

## Overview

Modern, professional web UI built with Next.js 14, TypeScript, and shadcn/ui component library.

## Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **shadcn/ui** - Professional UI components built on Radix UI
- **Tailwind CSS v3** - Utility-first styling
- **next-themes** - Dark mode support
- **React Markdown** - Message rendering with GitHub Flavored Markdown

## Running the Frontend

```bash
cd frontend-v2
npm run dev
```

Access at: **http://localhost:3006**

## Features

### ✅ Complete Implementation

- **WebSocket Chat** - Real-time agent communication via `ws://localhost:8000/ws`
- **Dark Mode** - Toggle between light/dark themes (defaults to dark)
- **Velocity Agent Branding** - Custom styling with Infoblox green (#00A982)
- **System Status** - Live display of MCP servers, agents, and tools
- **TypeScript** - Full type safety with interfaces
- **Accessible UI** - Radix UI primitives for WCAG compliance
- **Responsive Design** - Mobile-friendly layout
- **Auto-growing Textarea** - Expands as you type
- **Message History** - Persistent chat with clear button
- **Tool Call Visualization** - See agent tool usage in real-time
- **Example Prompts** - Quick-start templates for common tasks

### Component Architecture

```
frontend-v2/
├── app/
│   ├── page.tsx          # Main application page
│   ├── layout.tsx        # Root layout with ThemeProvider
│   └── globals.css       # Tailwind + theme configuration
├── components/
│   ├── sidebar.tsx       # Left sidebar with status & branding
│   ├── chat.tsx          # Chat interface component
│   ├── message.tsx       # Individual message renderer
│   ├── theme-provider.tsx # Dark mode provider
│   └── ui/               # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── badge.tsx
│       ├── separator.tsx
│       └── scroll-area.tsx
├── hooks/
│   └── use-websocket.ts  # WebSocket client hook
└── lib/
    └── utils.ts          # Utility functions (cn)
```

## Configuration

### Tailwind Theme

Infoblox green color scheme configured in `app/globals.css`:

```css
:root {
  --primary: 168 100% 33%;      /* #00A982 */
  --secondary: 168 100% 28%;    /* Darker green */
  --infoblox-green: 168 100% 33%;
  --infoblox-dark: 168 100% 27.5%;
}
```

### WebSocket Connection

Connects to FastAPI backend at `ws://localhost:8000/ws`

- Auto-reconnects on disconnect
- Status indicator (Connected/Disconnected)
- Real-time message streaming
- Agent selection support

### Next.js Configuration

- **Turbopack** enabled for fast development
- **Dark mode** via class strategy
- **TypeScript** strict mode
- **ESLint** configured

## Development Commands

```bash
# Install dependencies
npm install

# Start development server (port 3006)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Backend Integration

The frontend connects to the FastAPI backend running on port 8000:

- **WebSocket**: `ws://localhost:8000/ws` - Real-time chat
- **System Status**: `http://localhost:8000/api/status` - Server info
- **Agents List**: `http://localhost:8000/api/agents` - Available agents

Make sure the backend is running before starting the frontend.

## Production Deployment

### Option 1: Self-Hosted (Node.js)

1. **Build the production bundle:**
```bash
cd frontend-v2
npm run build
```

2. **Start the production server:**
```bash
npm start
```

The production build will be optimized and ready to serve on port 3006 (or custom port via `PORT` env var).

### Option 2: Vercel (Recommended)

Vercel is the creators of Next.js and provides the best hosting experience:

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Deploy:**
```bash
cd frontend-v2
vercel
```

3. **Configure Environment Variables:**
   - Add backend WebSocket URL as environment variable
   - Update `use-websocket.ts` to use production backend URL

**Production Configuration:**
```typescript
// hooks/use-websocket.ts - Update for production
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'localhost:8000';
const wsUrl = `wss://${backendUrl}/ws`;  // Use wss:// for production
```

**Vercel Environment Variables:**
- `NEXT_PUBLIC_BACKEND_URL`: Your FastAPI backend domain (e.g., `api.yourdomain.com`)

### Option 3: Docker

1. **Create Dockerfile:**
```dockerfile
# frontend-v2/Dockerfile
FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Build application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3006

ENV PORT=3006

CMD ["node", "server.js"]
```

2. **Build and run:**
```bash
cd frontend-v2
docker build -t velocity-agent-frontend .
docker run -p 3006:3006 \
  -e NEXT_PUBLIC_BACKEND_URL=your-backend-url \
  velocity-agent-frontend
```

### Option 4: Netlify

1. **Install Netlify CLI:**
```bash
npm install -g netlify-cli
```

2. **Deploy:**
```bash
cd frontend-v2
netlify deploy --prod
```

3. **Configure:**
   - Build command: `npm run build`
   - Publish directory: `.next`
   - Add environment variables in Netlify dashboard

### Backend Integration for Production

Update your Next.js configuration to handle WebSocket connections:

**next.config.ts:**
```typescript
const nextConfig: NextConfig = {
  experimental: {
    turbo: {
      root: __dirname,
    },
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.BACKEND_URL + '/api/:path*',
      },
    ];
  },
};
```

### SSL/TLS Configuration

For production, ensure:
- Frontend uses `https://`
- WebSocket uses `wss://` (secure WebSocket)
- Backend FastAPI has SSL certificate
- CORS configured for production domain

**FastAPI CORS Setup:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Performance Optimization

The production build automatically includes:
- ✅ Code splitting
- ✅ Tree shaking
- ✅ Minification
- ✅ Image optimization
- ✅ Static generation where possible
- ✅ Incremental Static Regeneration (ISR)

### Monitoring

Consider adding:
- **Vercel Analytics**: Built-in performance monitoring
- **Sentry**: Error tracking
- **LogRocket**: Session replay
- **New Relic**: Application performance monitoring

## Troubleshooting

**Port already in use:**
```bash
# Change port in package.json or use:
PORT=3007 npm run dev
```

**WebSocket not connecting:**
- Verify backend is running on port 8000
- Check firewall settings
- Ensure no CORS issues

**Dark mode not working:**
- Clear browser cache
- Check localStorage for theme preference
- Verify next-themes provider in layout

**Styling issues:**
- Run `npm install` to ensure all dependencies
- Check Tailwind config is correct
- Verify globals.css is imported in layout

## Key Dependencies

```json
{
  "dependencies": {
    "next": "16.0.2",
    "react": "19.2.0",
    "next-themes": "^0.4.6",
    "react-markdown": "^10.1.0",
    "remark-gfm": "^4.0.1",
    "axios": "^1.13.2",
    "@radix-ui/react-*": "Latest"
  },
  "devDependencies": {
    "typescript": "^5",
    "tailwindcss": "^3.4.18",
    "autoprefixer": "^10.4.22",
    "postcss": "^8.5.6"
  }
}
```

## Architecture Benefits

- ✅ **Type Safety** - Catch errors at compile time
- ✅ **Component Reusability** - shadcn/ui components
- ✅ **Performance** - Next.js optimizations
- ✅ **SEO Ready** - Server-side rendering support
- ✅ **Accessibility** - WCAG compliant with Radix UI
- ✅ **Developer Experience** - Hot reload, TypeScript, ESLint
- ✅ **Maintainability** - Clean architecture, documented code
- ✅ **Scalability** - Easy to add new features
