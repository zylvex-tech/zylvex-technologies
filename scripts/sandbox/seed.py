#!/usr/bin/env python3
"""Zylvex Developer Sandbox — Seed CLI.

Usage:
    python seed.py users --count 20
    python seed.py anchors --count 100 --city lagos
    python seed.py mindmaps --count 15
    python seed.py all --reset
"""

import argparse
import json
import os
import random
import sys
import uuid
from pathlib import Path

try:
    import requests
    from faker import Faker
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print(
        "Missing dependencies. Install them with:\n"
        "  pip install -r scripts/sandbox/requirements.txt"
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8001")
SPATIAL_URL = os.getenv("SPATIAL_URL", "http://localhost:8000")
MINDMAP_URL = os.getenv("MINDMAP_URL", "http://localhost:8002")

STATE_FILE = Path(__file__).parent / "seed_state.json"

console = Console()
fake = Faker()

# ---------------------------------------------------------------------------
# City coordinates — 5 African + 3 global
# ---------------------------------------------------------------------------

CITIES = {
    "lagos": {"lat": 6.5244, "lng": 3.3792, "country": "Nigeria"},
    "nairobi": {"lat": -1.2921, "lng": 36.8219, "country": "Kenya"},
    "accra": {"lat": 5.6037, "lng": -0.1870, "country": "Ghana"},
    "cairo": {"lat": 30.0444, "lng": 31.2357, "country": "Egypt"},
    "cape_town": {"lat": -33.9249, "lng": 18.4241, "country": "South Africa"},
    "london": {"lat": 51.5074, "lng": -0.1278, "country": "UK"},
    "new_york": {"lat": 40.7128, "lng": -74.0060, "country": "USA"},
    "tokyo": {"lat": 35.6762, "lng": 139.6503, "country": "Japan"},
}

ANCHOR_CATEGORIES = ["landmark", "art", "note", "event", "memory", "guide"]
CONTENT_TYPES = ["text"]

MINDMAP_TEMPLATES = [
    {
        "title": "Product Strategy",
        "nodes": [
            {"text": "Product Strategy", "children": [
                {"text": "Market Research", "children": [
                    {"text": "Competitor Analysis"},
                    {"text": "Customer Interviews"},
                    {"text": "Market Size Estimation"},
                ]},
                {"text": "Product Vision", "children": [
                    {"text": "Core Value Proposition"},
                    {"text": "Target Audience"},
                ]},
                {"text": "Roadmap", "children": [
                    {"text": "Q1 Goals"},
                    {"text": "Q2 Goals"},
                    {"text": "Long-term Vision"},
                ]},
            ]},
        ],
    },
    {
        "title": "Study Notes: Physics",
        "nodes": [
            {"text": "Physics", "children": [
                {"text": "Mechanics", "children": [
                    {"text": "Newton's Laws"},
                    {"text": "Kinematics"},
                    {"text": "Energy & Work"},
                ]},
                {"text": "Electromagnetism", "children": [
                    {"text": "Coulomb's Law"},
                    {"text": "Magnetic Fields"},
                ]},
                {"text": "Thermodynamics", "children": [
                    {"text": "Laws of Thermodynamics"},
                    {"text": "Heat Transfer"},
                    {"text": "Entropy"},
                ]},
            ]},
        ],
    },
    {
        "title": "Creative Project",
        "nodes": [
            {"text": "Creative Project", "children": [
                {"text": "Concept", "children": [
                    {"text": "Mood Board"},
                    {"text": "Color Palette"},
                    {"text": "Typography"},
                ]},
                {"text": "Execution", "children": [
                    {"text": "Wireframes"},
                    {"text": "Prototypes"},
                ]},
                {"text": "Launch", "children": [
                    {"text": "Marketing Plan"},
                    {"text": "Social Media Strategy"},
                    {"text": "Press Kit"},
                ]},
            ]},
        ],
    },
    {
        "title": "Business Plan",
        "nodes": [
            {"text": "Business Plan", "children": [
                {"text": "Executive Summary", "children": [
                    {"text": "Mission Statement"},
                    {"text": "Key Metrics"},
                ]},
                {"text": "Financial Model", "children": [
                    {"text": "Revenue Streams"},
                    {"text": "Cost Structure"},
                    {"text": "Break-even Analysis"},
                ]},
                {"text": "Operations", "children": [
                    {"text": "Team Structure"},
                    {"text": "Technology Stack"},
                    {"text": "Partnerships"},
                ]},
            ]},
        ],
    },
]

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------


def load_state() -> dict:
    """Load seed state from disk."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"users": [], "anchors": [], "mindmaps": [], "tokens": {}}


def save_state(state: dict) -> None:
    """Persist seed state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def reset_state() -> dict:
    """Wipe seed state file and return fresh state."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    return {"users": [], "anchors": [], "mindmaps": [], "tokens": {}}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _post(url: str, json_data: dict, token: str | None = None) -> dict | None:
    """POST with connection-error handling."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.post(url, json=json_data, headers=headers, timeout=15)
        if resp.status_code in (200, 201):
            return resp.json()
        console.print(
            f"  [yellow]⚠ {resp.status_code}[/yellow] {url} — {resp.text[:200]}"
        )
        return None
    except requests.ConnectionError:
        console.print(
            f"  [red]✗ Connection refused:[/red] {url}\n"
            "    Make sure the service is running."
        )
        return None
    except requests.Timeout:
        console.print(f"  [red]✗ Request timed out:[/red] {url}")
        return None
    except requests.RequestException as exc:
        console.print(f"  [red]✗ Request error:[/red] {exc}")
        return None


def _get_token(state: dict) -> str | None:
    """Return a cached access token, registering+logging in a seed user if needed."""
    if state.get("tokens", {}).get("access_token"):
        return state["tokens"]["access_token"]

    # Create a seed admin user
    email = "seed-admin@zylvex.dev"
    password = "SeedAdmin123!"
    full_name = "Seed Admin"

    # Try login first (user may already exist)
    login_resp = _post(f"{AUTH_URL}/auth/login", {"email": email, "password": password})
    if login_resp and "access_token" in login_resp:
        state.setdefault("tokens", {})["access_token"] = login_resp["access_token"]
        save_state(state)
        return login_resp["access_token"]

    # Register
    reg_resp = _post(
        f"{AUTH_URL}/auth/register",
        {"email": email, "password": password, "full_name": full_name},
    )
    if not reg_resp:
        return None

    # Login
    login_resp = _post(f"{AUTH_URL}/auth/login", {"email": email, "password": password})
    if login_resp and "access_token" in login_resp:
        state.setdefault("tokens", {})["access_token"] = login_resp["access_token"]
        save_state(state)
        return login_resp["access_token"]

    return None


# ---------------------------------------------------------------------------
# Seed: users
# ---------------------------------------------------------------------------


def seed_users(count: int, state: dict) -> None:
    """Register *count* users via the auth service."""
    console.print(f"\n[bold cyan]🌱 Seeding {count} users …[/bold cyan]")
    created = 0
    for _ in range(count):
        email = fake.unique.email()
        payload = {
            "email": email,
            "password": "TestPass123!",
            "full_name": fake.name(),
        }
        resp = _post(f"{AUTH_URL}/auth/register", payload)
        if resp:
            state["users"].append(
                {"id": resp.get("id", str(uuid.uuid4())), "email": email}
            )
            created += 1
    save_state(state)
    console.print(f"  [green]✓ Created {created}/{count} users[/green]")


# ---------------------------------------------------------------------------
# Seed: anchors
# ---------------------------------------------------------------------------


def _jitter(val: float, spread: float = 0.02) -> float:
    """Add a small random offset to a coordinate."""
    return val + random.uniform(-spread, spread)


def seed_anchors(count: int, state: dict, city: str | None = None) -> None:
    """Create anchors via the Spatial Canvas API."""
    console.print(f"\n[bold cyan]📍 Seeding {count} anchors …[/bold cyan]")

    token = _get_token(state)
    if not token:
        console.print("  [red]✗ Cannot seed anchors — no auth token.[/red]")
        return

    if city:
        city_key = city.lower().replace(" ", "_")
        if city_key not in CITIES:
            console.print(
                f"  [red]✗ Unknown city '{city}'. "
                f"Choose from: {', '.join(CITIES.keys())}[/red]"
            )
            return
        target_cities = {city_key: CITIES[city_key]}
    else:
        target_cities = CITIES

    city_keys = list(target_cities.keys())
    created = 0

    for i in range(count):
        ck = city_keys[i % len(city_keys)]
        coords = target_cities[ck]
        category = random.choice(ANCHOR_CATEGORIES)
        payload = {
            "title": f"{fake.catch_phrase()} — {ck.replace('_', ' ').title()}",
            "content": fake.paragraph(nb_sentences=3),
            "content_type": random.choice(CONTENT_TYPES),
            "latitude": _jitter(coords["lat"]),
            "longitude": _jitter(coords["lng"]),
        }
        resp = _post(f"{SPATIAL_URL}/api/v1/anchors", payload, token=token)
        if resp:
            state["anchors"].append(
                {
                    "id": resp.get("id", str(uuid.uuid4())),
                    "city": ck,
                    "title": payload["title"],
                }
            )
            created += 1

    save_state(state)
    console.print(f"  [green]✓ Created {created}/{count} anchors[/green]")


# ---------------------------------------------------------------------------
# Seed: mindmaps
# ---------------------------------------------------------------------------


def _flatten_tree(
    nodes: list[dict],
    parent_api_id: str | None = None,
    x_offset: float = 0.0,
    y_offset: float = 0.0,
) -> list[dict]:
    """Flatten a nested node template into ordered API payloads."""
    result: list[dict] = []
    for idx, node in enumerate(nodes):
        x = x_offset + idx * 200.0
        y = y_offset
        entry = {
            "text": node["text"],
            "focus_level": random.randint(30, 95),
            "color": random.choice(
                ["#6C63FF", "#00BFA6", "#FF6F61", "#FFD93D", "#4FC3F7"]
            ),
            "x": x,
            "y": y,
            "parent_id": parent_api_id,
            "children": node.get("children", []),
        }
        result.append(entry)
    return result


def seed_mindmaps(count: int, state: dict) -> None:
    """Create mind maps with hierarchical nodes."""
    console.print(f"\n[bold cyan]🧠 Seeding {count} mind maps …[/bold cyan]")

    token = _get_token(state)
    if not token:
        console.print("  [red]✗ Cannot seed mind maps — no auth token.[/red]")
        return

    created = 0
    for i in range(count):
        template = MINDMAP_TEMPLATES[i % len(MINDMAP_TEMPLATES)]
        title = f"{template['title']} — {fake.bs().title()}"

        mm_resp = _post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            {"title": title},
            token=token,
        )
        if not mm_resp:
            continue

        mm_id = mm_resp["id"]

        # Build nodes depth-first
        _create_nodes_recursive(
            mm_id, template["nodes"], parent_id=None, token=token, depth=0
        )

        state["mindmaps"].append({"id": mm_id, "title": title})
        created += 1

    save_state(state)
    console.print(f"  [green]✓ Created {created}/{count} mind maps[/green]")


def _create_nodes_recursive(
    mm_id: str,
    nodes: list[dict],
    parent_id: str | None,
    token: str,
    depth: int,
) -> None:
    """Recursively create nodes via the API."""
    for idx, node in enumerate(nodes):
        payload = {
            "text": node["text"],
            "focus_level": random.randint(30, 95),
            "color": random.choice(
                ["#6C63FF", "#00BFA6", "#FF6F61", "#FFD93D", "#4FC3F7"]
            ),
            "x": float(idx * 220 + depth * 50),
            "y": float(depth * 150),
            "parent_id": parent_id,
        }
        resp = _post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{mm_id}/nodes",
            payload,
            token=token,
        )
        if resp and node.get("children"):
            _create_nodes_recursive(
                mm_id, node["children"], resp["id"], token, depth + 1
            )


# ---------------------------------------------------------------------------
# Sub-command: all
# ---------------------------------------------------------------------------


def seed_all(reset: bool, state: dict) -> None:
    """Seed everything. Optionally reset first."""
    if reset:
        console.print("[bold red]🗑  Resetting seed state …[/bold red]")
        state = reset_state()

    seed_users(20, state)
    seed_anchors(100, state)
    seed_mindmaps(15, state)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Zylvex Developer Sandbox — data seeder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python seed.py users --count 20\n"
            "  python seed.py anchors --count 100 --city lagos\n"
            "  python seed.py mindmaps --count 15\n"
            "  python seed.py all --reset\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # users
    p_users = sub.add_parser("users", help="Seed user accounts")
    p_users.add_argument("--count", type=int, default=20, help="Number of users")

    # anchors
    p_anchors = sub.add_parser("anchors", help="Seed spatial anchors")
    p_anchors.add_argument("--count", type=int, default=100, help="Number of anchors")
    p_anchors.add_argument(
        "--city",
        type=str,
        default=None,
        help="Restrict to a city (lagos, nairobi, accra, cairo, cape_town, london, new_york, tokyo)",
    )

    # mindmaps
    p_mm = sub.add_parser("mindmaps", help="Seed mind maps with node trees")
    p_mm.add_argument("--count", type=int, default=15, help="Number of mind maps")

    # all
    p_all = sub.add_parser("all", help="Seed users + anchors + mindmaps")
    p_all.add_argument(
        "--reset",
        action="store_true",
        help="Wipe seed_state.json and reseed from scratch",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    state = load_state()

    console.print("[bold magenta]🚀 Zylvex Developer Sandbox Seeder[/bold magenta]")

    if args.command == "users":
        seed_users(args.count, state)
    elif args.command == "anchors":
        seed_anchors(args.count, state, city=args.city)
    elif args.command == "mindmaps":
        seed_mindmaps(args.count, state)
    elif args.command == "all":
        seed_all(args.reset, state)

    console.print("\n[bold green]✅ Done![/bold green]")


if __name__ == "__main__":
    main()
