# Contributing to Zylvex Technologies

## Branch naming
Branches must follow one of these patterns:
- `feature/<description>` — new features
- `bugfix/<description>` — bug fixes
- `release/<version>` — release branches
- `chore/<description>` — maintenance, tooling, docs

The `copilot/*` prefix is reserved for automated agent sessions.

## Commit format (Conventional Commits)
`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`

## Pull requests
- Every PR must have a non-empty description
- All CI checks must pass before merge
- At least one review required for `main`

## Local development
One-command start: `docker compose -f docker-compose.full-stack.yml up --build`

Services:
| Service | URL |
|---|---|
| Auth | http://localhost:8001 |
| Spatial Canvas API | http://localhost:8000 |
| Mind Mapper API | http://localhost:8002 |

## Running tests
```bash
cd shared/auth && pip install -r requirements-dev.txt && pytest tests/ -v
cd spatial-canvas/backend && pip install -r requirements-dev.txt && pytest tests/ -v
cd mind-mapper/backend-services && pip install -r requirements-dev.txt && pytest tests/ -v
```
