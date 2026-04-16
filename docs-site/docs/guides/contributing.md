---
id: contributing
title: Contributing Guide
sidebar_label: Contributing
slug: /guides/contributing
---

# Contributing to Zylvex Technologies

Thank you for contributing! This guide covers branch naming, PR process, commit message format, and code style.

## Getting Started

1. Fork the repository (external contributors) or clone directly (team members)
2. Create a branch following the naming convention below
3. Make your changes
4. Run tests and linting
5. Open a Pull Request

---

## Branch Naming Convention

All branches must match one of these patterns (enforced by `pr-checks.yml`):

| Pattern | Use Case | Example |
|---------|----------|---------|
| `feature/*` | New features | `feature/anchor-media-uploads` |
| `bugfix/*` | Bug fixes | `bugfix/fix-radius-search-accuracy` |
| `fix/*` | Small fixes | `fix/typo-in-error-message` |
| `release/*` | Release preparation | `release/v1.2.0` |
| `chore/*` | Maintenance, deps, CI | `chore/update-fastapi-0.110` |
| `copilot/*` | AI-assisted changes | `copilot/add-email-verification` |

:::warning
PRs from branches that don't match these patterns will fail the CI `pr-checks.yml` workflow.
:::

---

## Commit Message Format

Zylvex uses **Conventional Commits**:

```
<type>(<scope>): <short description>

[optional body]

[optional footer: Closes #123]
```

### Types

| Type | When to Use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code change with no feature/fix |
| `chore` | Build process, dependencies, CI/CD |
| `perf` | Performance improvement |

### Examples

```bash
feat(auth): add email verification on registration
fix(spatial): correct degree-to-km radius conversion at high latitudes
docs(api): add BCI session endpoint examples
test(social): add 4 tests for trending feed edge cases
chore(deps): upgrade fastapi to 0.110.0
```

---

## Pull Request Process

### PR Requirements

- [ ] Non-empty description explaining **what** and **why**
- [ ] Tests for any new functionality
- [ ] All CI checks pass (green)
- [ ] No unrelated changes snuck in

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Changed X to fix Y
- Added Z endpoint

## Testing
- Added N tests covering X, Y, Z
- All existing tests pass

## Related Issues
Closes #123
```

### CI Checks (Enforced)

The `pr-checks.yml` workflow enforces:
- **Non-empty PR description** — blank PRs are blocked
- **Branch naming** — must match allowed patterns
- **Python linting** — `black` (formatting) + `flake8` (linting)

### Review

- Requires at least **1 approval** before merging
- Address all review comments before merging
- Use squash-merge for small PRs; merge commit for large features

---

## Code Style

### Python (all backend services)

```bash
# Format with black (default config)
black shared/auth/

# Lint with flake8 (max line length 100)
flake8 shared/auth/ --max-line-length=100

# Sort imports
isort shared/auth/
```

### TypeScript (web app and mobile)

```bash
cd web-app
npm run lint        # ESLint
npm run type-check  # TypeScript compiler check
```

---

## Architecture Rules (Do Not Break)

1. **Never verify JWTs locally** in downstream services. Always call `GET /auth/verify` on the auth service at `:8001`.
2. **Use Alembic migrations** for all DB schema changes. Never modify the database directly.
3. **Never hardcode secrets** — use environment variables. Add new vars to `.env.example`.
4. **CORS** — always use the `ALLOWED_ORIGINS` env var. Never use `*` in production.
5. **Service ports** — Auth: 8001, SC: 8000, MM: 8002, Social: 8003, Realtime: 8004, Notifications: 8005. Changing these requires updating docker-compose and all documentation.

---

## Running CI Checks Locally

```bash
# Python — auth service
cd shared/auth
black --check .
flake8 . --max-line-length=100
pytest tests/ -v

# TypeScript — web app
cd web-app
npm run lint
npm run type-check
```

---

## Release Process

1. Create a `release/vX.Y.Z` branch from `main`
2. Update version numbers and CHANGELOG
3. Open a PR titled `chore(release): vX.Y.Z`
4. After approval, merge to `main`
5. Tag the merge commit: `git tag vX.Y.Z && git push --tags`
6. The `deploy-staging.yml` workflow deploys tagged commits automatically
