#!/usr/bin/env python3
"""Zylvex Developer Sandbox — Notebook Data Generator.

Generates the same synthetic datasets used in the Jupyter notebooks and exports
them to docs/notebooks/data/ as JSON files so notebooks can optionally load
real-seeded data instead of hardcoded samples.

Usage:
    python generate_notebook_data.py
"""

import json
import math
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from faker import Faker
    from rich.console import Console
except ImportError:
    print(
        "Missing dependencies. Install them with:\n"
        "  pip install -r scripts/sandbox/requirements.txt"
    )
    sys.exit(1)


console = Console()
fake = Faker()

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "notebooks" / "data"

# ---------------------------------------------------------------------------
# City coordinates (matches seed.py)
# ---------------------------------------------------------------------------

CITIES = {
    "Lagos": {"lat": 6.5244, "lng": 3.3792},
    "Nairobi": {"lat": -1.2921, "lng": 36.8219},
    "Accra": {"lat": 5.6037, "lng": -0.1870},
    "Cairo": {"lat": 30.0444, "lng": 31.2357},
    "Cape Town": {"lat": -33.9249, "lng": 18.4241},
    "London": {"lat": 51.5074, "lng": -0.1278},
    "New York": {"lat": 40.7128, "lng": -74.0060},
    "Tokyo": {"lat": 35.6762, "lng": 139.6503},
}

ANCHOR_CATEGORIES = ["landmark", "art", "note", "event", "memory", "guide"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _jitter(val: float, spread: float = 0.03) -> float:
    return round(val + random.uniform(-spread, spread), 6)


def _uuid() -> str:
    return str(uuid.uuid4())


def _iso_date(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


# ---------------------------------------------------------------------------
# Spatial Canvas anchors (200 anchors across 8 cities)
# ---------------------------------------------------------------------------


def generate_anchors(count: int = 200) -> list[dict]:
    """Generate synthetic anchor data matching notebook expectations."""
    anchors = []
    city_names = list(CITIES.keys())
    for i in range(count):
        city = city_names[i % len(city_names)]
        coords = CITIES[city]
        anchors.append({
            "id": _uuid(),
            "user_id": _uuid(),
            "title": fake.catch_phrase(),
            "content": fake.paragraph(nb_sentences=2),
            "content_type": "text",
            "category": random.choice(ANCHOR_CATEGORIES),
            "latitude": _jitter(coords["lat"]),
            "longitude": _jitter(coords["lng"]),
            "reactions": random.randint(0, 150),
            "created_at": _iso_date(random.randint(0, 90)),
            "city": city,
        })
    return anchors


# ---------------------------------------------------------------------------
# Mind Map nodes (25-node hierarchical tree)
# ---------------------------------------------------------------------------


def generate_mindmap_tree() -> dict:
    """Generate a single 25-node hierarchical mind-map tree."""
    nodes: list[dict] = []

    def _add_node(
        text: str,
        parent_id: str | None,
        depth: int,
        x: float,
        y: float,
    ) -> str:
        nid = _uuid()
        nodes.append({
            "id": nid,
            "text": text,
            "parent_id": parent_id,
            "focus_level": random.randint(20, 95),
            "color": random.choice(
                ["#6C63FF", "#00BFA6", "#FF6F61", "#FFD93D", "#4FC3F7"]
            ),
            "x": x,
            "y": y,
            "depth": depth,
        })
        return nid

    root_id = _add_node("Product Strategy", None, 0, 400, 50)

    l1_topics = ["Market Research", "Product Vision", "Roadmap", "Metrics", "Team"]
    for i, topic in enumerate(l1_topics):
        l1_id = _add_node(topic, root_id, 1, 100 + i * 180, 200)
        subtopics = [fake.bs().title() for _ in range(random.randint(2, 4))]
        for j, sub in enumerate(subtopics):
            _add_node(sub, l1_id, 2, 100 + i * 180 + j * 60, 350)
            if len(nodes) >= 25:
                break
        if len(nodes) >= 25:
            break

    return {
        "id": _uuid(),
        "title": "Product Strategy",
        "user_id": _uuid(),
        "created_at": _iso_date(10),
        "nodes": nodes[:25],
    }


# ---------------------------------------------------------------------------
# BCI focus sessions (5 sessions × 600 data points each)
# ---------------------------------------------------------------------------


def generate_bci_sessions(session_count: int = 5, points: int = 600) -> list[dict]:
    """Generate synthetic BCI focus sessions."""
    sessions = []
    for s in range(session_count):
        timeline: list[float] = []
        base = random.uniform(40, 65)
        for t in range(points):
            # Simulate focus with sine wave + noise + drift
            drift = (t / points) * random.uniform(-10, 15)
            wave = 10 * math.sin(2 * math.pi * t / random.uniform(80, 150))
            noise = random.gauss(0, 5)
            val = max(0, min(100, base + drift + wave + noise))
            timeline.append(round(val, 2))

        avg_focus = round(sum(timeline) / len(timeline), 2)
        sessions.append({
            "id": _uuid(),
            "mindmap_id": _uuid(),
            "session_index": s + 1,
            "avg_focus": avg_focus,
            "duration_seconds": random.randint(300, 1800),
            "node_count": random.randint(5, 25),
            "focus_timeline": timeline,
            "created_at": _iso_date(random.randint(0, 30)),
        })
    return sessions


# ---------------------------------------------------------------------------
# Users (for completeness)
# ---------------------------------------------------------------------------


def generate_users(count: int = 50) -> list[dict]:
    """Generate synthetic user profiles."""
    users = []
    for _ in range(count):
        users.append({
            "id": _uuid(),
            "email": fake.unique.email(),
            "full_name": fake.name(),
            "is_active": True,
            "is_verified": random.choice([True, False]),
            "created_at": _iso_date(random.randint(0, 120)),
        })
    return users


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    console.print(
        "[bold magenta]📊 Zylvex Notebook Data Generator[/bold magenta]\n"
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "anchors.json": generate_anchors(200),
        "mindmap_tree.json": generate_mindmap_tree(),
        "bci_sessions.json": generate_bci_sessions(5, 600),
        "users.json": generate_users(50),
    }

    for filename, data in datasets.items():
        path = OUTPUT_DIR / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        record_count = len(data) if isinstance(data, list) else 1
        console.print(
            f"  [green]✓[/green] {filename:<25} "
            f"({record_count:>3} records) → {path}"
        )

    console.print(
        f"\n[bold green]✅ Exported {len(datasets)} datasets "
        f"to {OUTPUT_DIR}/[/bold green]\n"
    )


if __name__ == "__main__":
    main()
