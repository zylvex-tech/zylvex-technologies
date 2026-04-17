"""E2E tests for the authentication flow (8 scenarios)."""

import pytest

from conftest import (
    AUTH_URL,
    auth_headers,
    login_user,
    register_user,
)


class TestAuthFlow:
    """Full authentication E2E scenarios."""

    # 1 ── Register new user → 201
    def test_register_new_user(self, http_client, unique_email):
        resp = register_user(http_client, email=unique_email)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data or "email" in data

    # 2 ── Register duplicate email → 409
    def test_register_duplicate_email(self, http_client, unique_email):
        register_user(http_client, email=unique_email)
        resp = register_user(http_client, email=unique_email)
        assert resp.status_code == 409

    # 3 ── Login with wrong password → 401
    def test_login_wrong_password(self, http_client, registered_user):
        email, _, _ = registered_user
        resp = login_user(http_client, email, password="WrongPassword999!")
        assert resp.status_code == 401

    # 4 ── Login success → access + refresh token
    def test_login_success(self, http_client, registered_user):
        email, password, _ = registered_user
        resp = login_user(http_client, email, password)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    # 5 ── Refresh token → new access token
    def test_refresh_token(self, http_client, authenticated_user):
        _, _, _, refresh_token = authenticated_user
        resp = http_client.post(
            f"{AUTH_URL}/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    # 6 ── Logout → refresh token invalidated
    def test_logout_invalidates_refresh_token(self, http_client, authenticated_user):
        _, _, access_token, refresh_token = authenticated_user
        # Logout
        resp = http_client.post(
            f"{AUTH_URL}/auth/logout",
            json={"refresh_token": refresh_token},
            headers=auth_headers(access_token),
        )
        assert resp.status_code == 200
        # Attempt refresh with revoked token
        resp = http_client.post(
            f"{AUTH_URL}/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 401

    # 7 ── Access protected endpoint without token → 401
    def test_protected_endpoint_no_token(self, http_client):
        resp = http_client.get(f"{AUTH_URL}/auth/me")
        assert resp.status_code in (401, 403)

    # 8 ── Access protected endpoint with valid token → 200
    def test_protected_endpoint_with_token(self, http_client, authenticated_user):
        _, _, access_token, _ = authenticated_user
        resp = http_client.get(
            f"{AUTH_URL}/auth/me",
            headers=auth_headers(access_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "email" in data
