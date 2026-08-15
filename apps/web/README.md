# apps/web — React + TypeScript frontend

Vite + React 18 + TypeScript SPA, Tailwind CSS, mobile-first. Talks to the
FastAPI backend over REST (and WebSocket, from Phase 2 onward).

Requires **Node.js 20+** locally. This repo was scaffolded on a machine
without Node installed, so typecheck/lint/test/build were verified inside
the `web` container (`docker compose exec web npm run <script>`) rather than
on the host — use `docker compose up` from the repo root if your machine
doesn't have Node either.

## Run locally without Docker

```bash
npm install
cp .env.example .env   # sets VITE_API_URL if not http://localhost:8000
npm run dev
```

http://localhost:5173

## Tests

```bash
npm run test        # Vitest + React Testing Library
npm run e2e          # Playwright (requires the API + web dev server running)
npm run typecheck
npm run lint
```

## Structure

```
src/
├── api/client.ts          fetch wrapper: bearer token in memory, httpOnly
│                           refresh cookie, transparent 401 -> refresh retry
├── features/auth/         auth-context.ts, AuthProvider, useAuth, Login/RegisterPage
├── routes/                ProtectedRoute, page components
```
