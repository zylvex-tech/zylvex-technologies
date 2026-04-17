"""Locust load test scenarios for Zylvex platform.

Run:
    locust -f locustfile.py --host http://localhost
    # Or headless:
    locust -f locustfile.py --host http://localhost --headless -u 100 -r 10 -t 5m
"""

import random
import uuid

from locust import HttpUser, between, tag, task


class ZylvexUser(HttpUser):
    """Simulates a typical Zylvex platform user.

    Task weights model a read-heavy workload:
      60% — GET nearby anchors
      20% — GET mind map tree
      15% — POST create anchor
       5% — POST login
    """

    wait_time = between(1, 3)

    # Service ports (mapped via host or docker networking)
    AUTH_PORT = 8001
    SPATIAL_PORT = 8000
    MINDMAP_PORT = 8002

    def on_start(self):
        """Register and login to obtain an access token."""
        self.email = f"load-{uuid.uuid4().hex[:12]}@zylvex-test.io"
        self.password = "LoadTest123!"

        # Register
        self.client.post(
            f":{self.AUTH_PORT}/auth/register",
            json={
                "email": self.email,
                "password": self.password,
                "full_name": f"Load User {uuid.uuid4().hex[:6]}",
            },
            name="/auth/register",
        )

        # Login
        resp = self.client.post(
            f":{self.AUTH_PORT}/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login",
        )
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get("access_token", "")
        else:
            self.token = ""

        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Create a mind map and anchor for subsequent reads
        self._seed_data()

    def _seed_data(self):
        """Create initial data so GET endpoints have content to return."""
        self.map_id = None
        self.anchor_ids: list[str] = []

        # Create a mind map
        resp = self.client.post(
            f":{self.MINDMAP_PORT}/api/v1/mindmaps",
            json={"title": f"Load Map {uuid.uuid4().hex[:6]}"},
            headers=self.headers,
            name="/api/v1/mindmaps [seed]",
        )
        if resp.status_code == 201:
            self.map_id = resp.json().get("id")

        # Create a couple of anchors
        for _ in range(2):
            lat = 6.5244 + random.uniform(-0.05, 0.05)
            lng = 3.3792 + random.uniform(-0.05, 0.05)
            resp = self.client.post(
                f":{self.SPATIAL_PORT}/api/v1/anchors",
                json={
                    "title": f"Load Anchor {uuid.uuid4().hex[:6]}",
                    "description": "Load test anchor",
                    "content_type": "text",
                    "latitude": lat,
                    "longitude": lng,
                },
                headers=self.headers,
                name="/api/v1/anchors [seed]",
            )
            if resp.status_code == 201:
                self.anchor_ids.append(resp.json().get("id", ""))

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    @tag("read", "spatial")
    @task(60)
    def get_nearby_anchors(self):
        """GET nearby anchors — 60% weight (read-heavy)."""
        lat = 6.5244 + random.uniform(-0.02, 0.02)
        lng = 3.3792 + random.uniform(-0.02, 0.02)
        self.client.get(
            f":{self.SPATIAL_PORT}/api/v1/anchors/nearby",
            params={"latitude": lat, "longitude": lng, "radius_km": 5},
            headers=self.headers,
            name="/api/v1/anchors/nearby",
        )

    @tag("read", "mindmap")
    @task(20)
    def get_mindmap_tree(self):
        """GET mind map tree — 20% weight."""
        if not self.map_id:
            return
        self.client.get(
            f":{self.MINDMAP_PORT}/api/v1/mindmaps/{self.map_id}",
            headers=self.headers,
            name="/api/v1/mindmaps/[id]",
        )

    @tag("write", "spatial")
    @task(15)
    def create_anchor(self):
        """POST create anchor — 15% weight."""
        lat = 6.5244 + random.uniform(-0.1, 0.1)
        lng = 3.3792 + random.uniform(-0.1, 0.1)
        self.client.post(
            f":{self.SPATIAL_PORT}/api/v1/anchors",
            json={
                "title": f"Anchor {uuid.uuid4().hex[:6]}",
                "description": "Load test",
                "content_type": "text",
                "latitude": lat,
                "longitude": lng,
            },
            headers=self.headers,
            name="/api/v1/anchors [create]",
        )

    @tag("auth")
    @task(5)
    def login(self):
        """POST login — 5% weight."""
        self.client.post(
            f":{self.AUTH_PORT}/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login",
        )
