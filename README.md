# Fantasy Baseball — Resume-Driven Full-Stack Project

A mobile-first fantasy baseball web app with a Python backend. This repo is a
deliberate portfolio project: the architecture was chosen to close specific
gaps in a resume that's strong on embedded systems, C/C#/Python, Docker,
CI/CD, and rigorous testing, but light on frontend frameworks, cloud infra
beyond AWS S3, real-time systems, and auth/security work.

See [`docs/adr/`](docs/adr/) for the reasoning behind key decisions as they're
made — treat these as interview material, not just documentation.

## Architecture

```
 React + TS (Vite, Tailwind)  ──REST + WebSocket──▶  FastAPI (async SQLAlchemy 2.0)
        SPA, mobile-first                                    │
                                                               ├─▶ Postgres (RDS)
                                                               └─▶ Redis (ElastiCache)
                                                                     cache + Pub/Sub

 Background worker(s) poll live MLB stats → publish scoring deltas on Redis
 Pub/Sub → FastAPI WebSocket endpoints fan out to connected clients.

 Infra: AWS ECS/Fargate + RDS + ElastiCache + ALB + S3/CloudFront,
 provisioned via Terraform. CI/CD via GitHub Actions.
```

- **Frontend**: React + TypeScript (Vite), Tailwind CSS, mobile-first SPA.
- **Backend**: FastAPI, async SQLAlchemy 2.0, Pydantic v2, JWT auth
  (short-lived access token + rotating httpOnly refresh cookie — see
  [ADR-0001](docs/adr/0001-jwt-over-sessions.md)).
- **Data**: Postgres (RDS), Redis (ElastiCache) as cache and Pub/Sub bus.
- **Real-time**: a background worker polls live MLB stats and publishes
  scoring deltas over Redis Pub/Sub; WebSocket endpoints push them to
  connected clients for live draft + live scoring.
- **Infra**: AWS (ECS/Fargate, RDS, ElastiCache, ALB, S3+CloudFront),
  provisioned with Terraform.
- **CI/CD**: GitHub Actions — lint + test gating on every PR.
- **Testing**: pytest + httpx (API), React Testing Library (components),
  Playwright at mobile viewport sizes (E2E).

## Repo layout

```
apps/api/     FastAPI backend (see apps/api/README.md)
apps/web/     React + Vite + TS frontend (see apps/web/README.md)
infra/terraform/  AWS infra as code (see infra/terraform/README.md)
docs/adr/     Architecture decision records
```

## Roadmap

| Phase | Builds | Resume gap it closes |
|---|---|---|
| **0 — Foundations** *(this scaffold)* | Monorepo, FastAPI + async SQLAlchemy skeleton, JWT auth, React/Vite/TS/Tailwind skeleton, docker-compose, CI, minimal Terraform (VPC/ECR/Fargate health check) | React/TS from zero, Terraform/IaC basics, ECS/Fargate, async FastAPI, auth design |
| 1 — Core domain | League/team/roster CRUD, nightly MLB Stats API sync, full AWS deploy (RDS, ElastiCache, ALB, CloudFront) | RDS, ElastiCache, CloudFront/S3, external API integration |
| 2 — Live draft room | WebSocket snake draft, turn timer, autopick, Redis Pub/Sub fan-out across ECS tasks | WebSockets, real-time state machines, distributed fan-out |
| 3 — Live scoring engine | Worker polling live MLB feeds → per-league scoring deltas → Redis Pub/Sub → WebSocket → live scoreboard | Background workers, decoupled ingestion/delivery, system-design-at-scale |
| 4 — Standings/waivers/trades | Weekly rollover, FAAB waivers, trade workflow | Scheduled background tasks, transactional business logic |
| 5 — Hardening | Full CI test suites, CloudWatch dashboards/alarms, structured logging, rate limiting, Secrets Manager, security pass | Observability, production security posture |

**MVP milestone** (end of Phase 3): one league, live WebSocket draft, real
MLB player pool, live WebSocket scoring during real games, mobile-responsive,
deployed on Terraform-provisioned AWS, JWT auth.

**Stretch** (pick selectively later): EKS/Kubernetes migration from ECS,
React Native/Capacitor wrapper, DynamoDB-backed draft event log, Prometheus/
Grafana, multi-region deploy, Google OAuth login.

**Deliberately out of scope for this project**: DS&A/interview coding prep,
behavioral prep, formal system-design mock interviews — this project supplies
material and vocabulary for those conversations, not reps at them.

## Local development

```bash
cp apps/api/.env.example apps/api/.env
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`, health at `/api/v1/health`)
- Web: http://localhost:5173

See `apps/api/README.md` and `apps/web/README.md` for running each service
outside Docker.

## Status

Phase 0 (foundations) scaffold. Terraform is written but **not yet applied**
— see `infra/terraform/README.md`.
