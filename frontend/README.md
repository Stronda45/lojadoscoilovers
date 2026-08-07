# frontend

React + Vite. Ver `../docs/FRONTEND.md` pra decisões de stack.

## Setup

```bash
cp .env.example .env   # ajuste VITE_API_BASE_URL se o backend não estiver em localhost:8000
npm install
npm run dev             # http://localhost:5173
```

Precisa do backend rodando (`../backend`, ver `../backend/README.md`) e com
`http://localhost:5173` em `CORS_ALLOWED_ORIGINS` no `.env` do backend.
