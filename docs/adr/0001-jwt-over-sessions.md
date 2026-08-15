# ADR-0001: JWT auth (rotating refresh) instead of server sessions

## Status
Accepted — Phase 0.

## Context
The app will run as multiple stateless ECS/Fargate tasks behind an ALB, with
no shared in-process memory between tasks. Auth needs to work correctly no
matter which task instance handles a given request, without requiring sticky
sessions at the load balancer (which would fight autoscaling and complicate
deploys/rolling restarts).

Two mainstream options:

1. **Server-side sessions** (session ID in a cookie, session state in
   Postgres/Redis) — simple mental model, easy to revoke, but every request
   needs a session-store lookup, and it couples auth to a specific storage
   backend being reachable.
2. **JWT** (stateless, signed token carrying claims) — no per-request store
   lookup to validate a token, verification is just a signature check, and it
   scales horizontally for free.

## Decision
Use JWT: a short-lived (15 min) access token returned to the client and
attached as a `Bearer` header on API calls, plus a longer-lived (7 day)
refresh token stored in an **httpOnly, `Secure`, `SameSite=Strict` cookie**
(not localStorage, to reduce XSS exposure). Refresh tokens are **rotated** on
every use (old one invalidated, new one issued) and can be revoked early via
a Redis-backed blocklist keyed by token ID (`jti`) — this gets most of the
revocability of sessions without a lookup on the hot path (every normal
request only needs to verify the short-lived access token, not check Redis).

## Consequences
- Access-token verification is O(1) local signature check — no DB/Redis
  round-trip on the common path, which matters once there are multiple
  Fargate tasks and Redis is also carrying Pub/Sub traffic for live scoring.
- Refresh/revocation still touches Redis, but only on the much less frequent
  refresh path, not on every request.
- Logout / "sign out everywhere" is implemented by blocklisting the
  refresh token's `jti`, not by deleting a session record.
- This is more moving parts than sessions for an app this size — accepted
  deliberately as a resume-relevant pattern (stateless auth for a
  horizontally-scaled service), not because it's the minimum-effort choice.
- Google OAuth2 (planned as a later add-on) fits on top of this cleanly: it
  becomes just another way to mint the same JWT pair.
