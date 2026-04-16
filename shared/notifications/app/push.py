"""
Push notification stub.

Logs to console for now.
TODO: replace the body of `send_push_notification` with real APNs / FCM delivery:
  - APNs (Apple Push Notification service): use the `httpx` async client with
    the APNs HTTP/2 API (https://developer.apple.com/documentation/usernotifications).
    Library suggestion: `aioapns` or `PyAPNs2`.
  - FCM (Firebase Cloud Messaging): call the FCM v1 API via httpx with an
    OAuth2 service-account token.
    Library suggestion: `firebase-admin` or direct httpx calls to
    https://fcm.googleapis.com/v1/projects/{project_id}/messages:send
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def send_push_notification(
    user_id: str,
    notification_type: str,
    title: str,
    body: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Send a push notification to a user's device(s).

    Currently stubs to a console log.

    To integrate APNs:
      1. Obtain the user's APNs device token from your token registry.
      2. Build an APNs payload with `aps.alert.title` and `aps.alert.body`.
      3. POST to https://api.push.apple.com/3/device/{device_token} using
         HTTP/2 with a valid APNs auth token (JWT signed with your .p8 key).

    To integrate FCM:
      1. Obtain the user's FCM registration token from your token registry.
      2. Obtain a Google OAuth2 access token using a service account JSON key.
      3. POST to https://fcm.googleapis.com/v1/projects/{project_id}/messages:send
         with `message.notification.title/body` and `message.token`.
    """
    logger.info(
        "[PUSH STUB] user_id=%s type=%s title=%r body=%r metadata=%s",
        user_id,
        notification_type,
        title,
        body,
        metadata,
    )
    # ─── APNs / FCM would be called here ──────────────────────────────────────
