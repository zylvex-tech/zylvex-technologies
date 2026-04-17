# 🧪 Zylvex Developer Sandbox

A set of CLI tools to quickly seed realistic data into your local Zylvex services for development and testing.

---

## Prerequisites

1. **Services must be running** — start the full stack first:
   ```bash
   docker compose -f docker-compose.full-stack.yml up -d
   ```
   Or run individual services:
   | Service | Default URL |
   |---------|------------|
   | Auth | `http://localhost:8001` |
   | Spatial Canvas | `http://localhost:8000` |
   | Mind Mapper | `http://localhost:8002` |

2. **Install sandbox dependencies:**
   ```bash
   pip install -r scripts/sandbox/requirements.txt
   ```

---

## Tools

### `seed.py` — Data Seeder CLI

Seed individual resource types or everything at once.

```bash
# Seed 20 users
python scripts/sandbox/seed.py users --count 20

# Seed 100 anchors across 8 cities
python scripts/sandbox/seed.py anchors --count 100

# Seed anchors for a specific city
python scripts/sandbox/seed.py anchors --count 50 --city lagos

# Seed 15 mind maps with hierarchical node trees
python scripts/sandbox/seed.py mindmaps --count 15

# Seed everything (20 users + 100 anchors + 15 mind maps)
python scripts/sandbox/seed.py all

# Reset and reseed from scratch
python scripts/sandbox/seed.py all --reset
```

**Supported cities:** Lagos, Nairobi, Accra, Cairo, Cape Town, London, New York, Tokyo

State is persisted in `seed_state.json` so repeated runs are additive.

### `demo.py` — One-Command Demo

Seeds all data (if not already seeded), prints a summary table, and shows curl commands to test the API.

```bash
python scripts/sandbox/demo.py
```

**Example output:**
```
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Resource      ┃ Count ┃ Sample ID                            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Users         │    20 │ a1b2c3d4-e5f6-7890-abcd-ef1234567890 │
│ Anchors       │   100 │ b2c3d4e5-f6a7-8901-bcde-f12345678901 │
│ Mind Maps     │    15 │ c3d4e5f6-a7b8-9012-cdef-123456789012 │
└───────────────┴───────┴──────────────────────────────────────┘

🧪 Test Commands:
1. Register a new user
2. Login and get tokens
3. Search nearby anchors (Lagos)
4. List my mind maps
5. Get mind map nodes
```

### `generate_notebook_data.py` — Notebook Dataset Generator

Generates synthetic datasets matching the Jupyter notebooks and exports them as JSON files.

```bash
python scripts/sandbox/generate_notebook_data.py
```

**Outputs to `docs/notebooks/data/`:**
| File | Contents |
|------|----------|
| `anchors.json` | 200 anchors across 8 cities |
| `mindmap_tree.json` | 25-node hierarchical mind map |
| `bci_sessions.json` | 5 BCI focus sessions × 600 data points |
| `users.json` | 50 synthetic user profiles |

Notebooks can load these files to use seeded data instead of hardcoded samples.

---

## Environment Variables

Override service URLs if your services run on non-default ports:

```bash
export AUTH_URL=http://localhost:8001
export SPATIAL_URL=http://localhost:8000
export MINDMAP_URL=http://localhost:8002
```

---

## Files

```
scripts/sandbox/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── seed.py                      # Main CLI seeder
├── demo.py                      # One-command demo launcher
├── generate_notebook_data.py    # Notebook dataset generator
└── seed_state.json              # Auto-generated state (git-ignored)
```
