# GitHub Workflows Guide

This folder contains the CI/CD workflows for Zylvex Technologies.

## Branch naming conventions

Pull requests are validated against these branch prefixes:

- `feature/*`
- `bugfix/*`
- `fix/*`
- `release/*`
- `chore/*`
- `copilot/*`

## Workflow triggers

| Workflow | Trigger |
| --- | --- |
| `pr-checks.yml` | Every pull request targeting `main` |
| `auth-ci.yml` | Push/PR changes under `shared/auth/**` |
| `spatial-canvas-ci.yml` | Push/PR changes under `spatial-canvas/backend/**` |
| `mobile-ci.yml` | Push/PR changes under `spatial-canvas/mobile/**` |
| `mind-mapper-ci.yml` | Push/PR changes under `mind-mapper/**` |
| `deploy-staging.yml` | Push to `main` (non-doc-only changes) |

## CI/CD pipeline stages

1. **PR Quality Gate (`pr-checks.yml`)**
   - Validates PR description
   - Validates branch naming
   - Detects changed services
   - Posts PR analysis comment
2. **Service CI workflows**
   - Run service-specific lint/tests/build
3. **Staging deployment**
   - Deploys to staging after `main` updates

## Troubleshooting common failures

### `fatal: ambiguous argument 'main'` (exit 128)
- Cause: `origin/main` is missing in the local checkout.
- Fix: fetch base refs before diff operations:
  - `git fetch --no-tags --prune origin +refs/heads/main:refs/remotes/origin/main`
- Fallback: use `HEAD~1..HEAD` when base ref is unavailable.

### `403 Resource not accessible by integration`
- Cause: missing/insufficient token permissions.
- Fix:
  - Ensure repository **Workflow permissions** are set appropriately.
  - Pass explicit token to actions that call GitHub APIs (for example `actions/github-script`).

### `429` rate-limit or quota exhaustion
- Cause: repeated/large AI-driven requests in automation.
- Fix:
  - Keep workflows deterministic and lightweight.
  - Avoid unnecessary AI calls in CI paths.
  - Use retries/backoff where external APIs are involved.

### Token/payload limit errors (`400`)
- Cause: overly large request payloads/prompts.
- Fix:
  - Reduce request size.
  - Limit context to changed files only.
  - Split large operations into smaller steps.
