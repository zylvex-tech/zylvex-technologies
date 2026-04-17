#!/usr/bin/env python3
"""Zylvex Developer Sandbox — One-Command Demo Launcher.

Seeds all data (if not already seeded) and prints a formatted summary table
plus curl commands to test the most interesting endpoints.

Usage:
    python demo.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
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
SEED_SCRIPT = Path(__file__).parent / "seed.py"

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_state() -> dict:
    """Load seed state from disk."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def already_seeded(state: dict) -> bool:
    """Check whether seed data already exists."""
    return bool(
        state.get("users")
        or state.get("anchors")
        or state.get("mindmaps")
    )


def run_seeder() -> None:
    """Run seed.py all to populate everything."""
    console.print("[bold cyan]🌱 Running seeder (seed.py all) …[/bold cyan]\n")
    result = subprocess.run(
        [sys.executable, str(SEED_SCRIPT), "all"],
        cwd=str(SEED_SCRIPT.parent),
    )
    if result.returncode != 0:
        console.print(
            "[bold red]✗ Seeder exited with errors. "
            "Check that services are running.[/bold red]"
        )


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------


def print_summary(state: dict) -> None:
    """Print a rich summary table of seeded data."""
    table = Table(
        title="🏗  Zylvex Sandbox — Seed Summary",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Resource", style="cyan", min_width=12)
    table.add_column("Count", justify="right", style="green")
    table.add_column("Sample ID", style="dim")

    users = state.get("users", [])
    anchors = state.get("anchors", [])
    mindmaps = state.get("mindmaps", [])

    table.add_row(
        "Users",
        str(len(users)),
        users[0]["id"] if users else "—",
    )
    table.add_row(
        "Anchors",
        str(len(anchors)),
        anchors[0]["id"] if anchors else "—",
    )
    table.add_row(
        "Mind Maps",
        str(len(mindmaps)),
        mindmaps[0]["id"] if mindmaps else "—",
    )

    console.print()
    console.print(table)


# ---------------------------------------------------------------------------
# Curl commands
# ---------------------------------------------------------------------------


def print_curl_commands(state: dict) -> None:
    """Print curl commands to test the 5 most interesting endpoints."""
    token = state.get("tokens", {}).get("access_token", "<YOUR_TOKEN>")
    anchors = state.get("anchors", [])
    mindmaps = state.get("mindmaps", [])

    commands = [
        {
            "description": "1. Register a new user",
            "curl": (
                f'curl -s -X POST {AUTH_URL}/auth/register \\\n'
                f'  -H "Content-Type: application/json" \\\n'
                f'  -d \'{{"email":"demo@zylvex.dev","password":"DemoPass123!","full_name":"Demo User"}}\''
            ),
        },
        {
            "description": "2. Login and get tokens",
            "curl": (
                f'curl -s -X POST {AUTH_URL}/auth/login \\\n'
                f'  -H "Content-Type: application/json" \\\n'
                f'  -d \'{{"email":"seed-admin@zylvex.dev","password":"SeedAdmin123!"}}\''
            ),
        },
        {
            "description": "3. Search nearby anchors (Lagos)",
            "curl": (
                f'curl -s "{SPATIAL_URL}/api/v1/anchors?latitude=6.5244&longitude=3.3792&radius_km=5"'
            ),
        },
        {
            "description": "4. List my mind maps",
            "curl": (
                f'curl -s {MINDMAP_URL}/api/v1/mindmaps \\\n'
                f'  -H "Authorization: Bearer {token}"'
            ),
        },
        {
            "description": (
                "5. Get mind map nodes"
                + (f" ({mindmaps[0]['id']})" if mindmaps else "")
            ),
            "curl": (
                f'curl -s {MINDMAP_URL}/api/v1/mindmaps/'
                f'{mindmaps[0]["id"] if mindmaps else "<MINDMAP_ID>"}/nodes \\\n'
                f'  -H "Authorization: Bearer {token}"'
            ),
        },
    ]

    console.print()
    console.print(
        Panel(
            "[bold]Try these curl commands to explore the API:[/bold]",
            title="🧪 Test Commands",
            border_style="blue",
        )
    )
    for cmd in commands:
        console.print(f"\n[bold yellow]{cmd['description']}[/bold yellow]")
        console.print(f"[dim]{cmd['curl']}[/dim]")

    console.print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    console.print(
        Panel(
            "[bold magenta]Zylvex Developer Sandbox — Demo Launcher[/bold magenta]\n"
            "Seeds data, prints summary, and shows test commands.",
            border_style="magenta",
        )
    )

    state = load_state()

    if already_seeded(state):
        console.print(
            "[green]✓ Seed data already exists. "
            "Skipping seeding (delete seed_state.json to reseed).[/green]"
        )
    else:
        run_seeder()
        state = load_state()

    print_summary(state)
    print_curl_commands(state)

    console.print(
        "[bold green]🎉 Demo ready! "
        "Copy-paste any curl command above to test.[/bold green]\n"
    )


if __name__ == "__main__":
    main()
