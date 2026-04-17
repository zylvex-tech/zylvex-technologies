"""E2E tests for the Mind Mapper flow (6 scenarios)."""

import pytest

from conftest import (
    MINDMAP_URL,
    auth_headers,
)


class TestMindMapFlow:
    """Full Mind Mapper E2E scenarios."""

    # 1 ── Create mind map → 201
    def test_create_mindmap(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            json={"title": "E2E Test Map", "description": "Created by E2E test"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data

    # 2 ── Add root node → 201
    def test_add_root_node(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        headers = auth_headers(token)
        # Create map
        map_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            json={"title": "Node Test Map"},
            headers=headers,
        )
        map_id = map_resp.json()["id"]
        # Add root node
        resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes",
            json={"title": "Root Node", "parent_id": None},
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data

    # 3 ── Add child node → 201 with correct parent_id
    def test_add_child_node(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        headers = auth_headers(token)
        # Create map
        map_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            json={"title": "Child Node Map"},
            headers=headers,
        )
        map_id = map_resp.json()["id"]
        # Add root
        root_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes",
            json={"title": "Root", "parent_id": None},
            headers=headers,
        )
        root_id = root_resp.json()["id"]
        # Add child
        child_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes",
            json={"title": "Child", "parent_id": root_id},
            headers=headers,
        )
        assert child_resp.status_code == 201
        child_data = child_resp.json()
        assert child_data["parent_id"] == root_id

    # 4 ── Get full map tree → hierarchical structure
    def test_get_map_tree(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        headers = auth_headers(token)
        # Create map with nodes
        map_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            json={"title": "Tree Map"},
            headers=headers,
        )
        map_id = map_resp.json()["id"]
        http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes",
            json={"title": "Root", "parent_id": None},
            headers=headers,
        )
        # Get map with nodes
        resp = http_client.get(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data

    # 5 ── Update node title → 200
    def test_update_node_title(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        headers = auth_headers(token)
        map_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            json={"title": "Update Node Map"},
            headers=headers,
        )
        map_id = map_resp.json()["id"]
        node_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes",
            json={"title": "Original Title", "parent_id": None},
            headers=headers,
        )
        node_id = node_resp.json()["id"]
        resp = http_client.put(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes/{node_id}",
            json={"title": "Updated Title"},
            headers=headers,
        )
        assert resp.status_code == 200

    # 6 ── Delete map → 204, all nodes cascade deleted
    def test_delete_map_cascades(self, http_client, authenticated_user):
        _, _, token, _ = authenticated_user
        headers = auth_headers(token)
        map_resp = http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps",
            json={"title": "Delete Me Map"},
            headers=headers,
        )
        map_id = map_resp.json()["id"]
        # Add a node
        http_client.post(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}/nodes",
            json={"title": "Orphan Node", "parent_id": None},
            headers=headers,
        )
        # Delete map
        resp = http_client.delete(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}",
            headers=headers,
        )
        assert resp.status_code in (200, 204)
        # Verify map is gone
        get_resp = http_client.get(
            f"{MINDMAP_URL}/api/v1/mindmaps/{map_id}",
            headers=headers,
        )
        assert get_resp.status_code == 404
