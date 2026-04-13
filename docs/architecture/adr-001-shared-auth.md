# ADR-001: Shared Authentication Service

## Status: Accepted

## Context
Multiple product backends (Spatial Canvas, Mind Mapper) need JWT authentication.

## Decision
A single shared FastAPI auth service at :8001 handles all registration, login, token issuance,
and token validation. Downstream services validate tokens by calling GET /auth/verify
(returns minimal identity) or GET /auth/me (returns full profile). No JWT verification
is performed locally in downstream services.

## Consequences
+ Single source of truth for user identities
+ Token rotation and revocation apply to all services simultaneously
- Every authenticated request requires an HTTP call to the auth service (latency)
- Auth service is a single point of failure for all authenticated requests
- No caching of validated tokens (future improvement: add TTL cache or Redis)
