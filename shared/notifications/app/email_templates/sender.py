"""
Email delivery via SendGrid API.

Only sends emails for: follow, reaction notification types.
Uses HTML templates with a dark-themed, Zylvex branded design.
"""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Notification types that trigger emails
EMAIL_NOTIFICATION_TYPES = frozenset({"follow", "reaction"})


def _build_html(title: str, body: str, cta_text: str = "", cta_url: str = "") -> str:
    """Render a dark-themed, Zylvex branded HTML email."""
    cta_block = ""
    if cta_text and cta_url:
        cta_block = f"""
        <div style="text-align:center;margin:32px 0;">
          <a href="{cta_url}"
             style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                    color:#fff;text-decoration:none;padding:12px 28px;
                    border-radius:8px;font-weight:600;font-size:15px;
                    display:inline-block;">
            {cta_text}
          </a>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#0a0a0f;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#13131a;border-radius:16px;
                      border:1px solid rgba(255,255,255,0.08);
                      overflow:hidden;max-width:560px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1e1b4b,#312e81);
                       padding:32px 40px;text-align:center;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                             border-radius:12px;width:44px;height:44px;
                             text-align:center;vertical-align:middle;">
                    <span style="color:#fff;font-size:22px;font-weight:700;
                                 line-height:44px;">Z</span>
                  </td>
                  <td style="padding-left:12px;vertical-align:middle;">
                    <span style="color:#e2e8f0;font-size:20px;font-weight:600;
                                 letter-spacing:-0.3px;">Zylvex</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <h1 style="color:#f1f5f9;font-size:22px;font-weight:700;
                         margin:0 0 16px;line-height:1.3;">
                {title}
              </h1>
              <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0 0 24px;">
                {body}
              </p>
              {cta_block}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#0d0d14;padding:20px 40px;
                       border-top:1px solid rgba(255,255,255,0.06);">
              <p style="color:#475569;font-size:12px;margin:0;text-align:center;">
                You received this email from
                <a href="https://zylvex.io"
                   style="color:#6366f1;text-decoration:none;">Zylvex Technologies</a>.
                <br />Manage your notification preferences in the app.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


async def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
) -> bool:
    """
    Send an HTML email via SendGrid.

    Returns True on success, False on failure (never raises).
    """
    if not settings.SENDGRID_API_KEY:
        logger.debug("SENDGRID_API_KEY not set — skipping email to %s", to_email)
        return False

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=Email(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
            to_emails=To(to_email, to_name),
            subject=subject,
            html_content=Content("text/html", html_content),
        )
        response = sg.send(message)
        if response.status_code in (200, 202):
            logger.info("Email sent to %s (subject: %s)", to_email, subject)
            return True
        logger.warning(
            "SendGrid returned %s for %s", response.status_code, to_email
        )
        return False
    except Exception as exc:
        logger.error("SendGrid error for %s: %s", to_email, exc)
        return False


async def maybe_send_notification_email(
    notification_type: str,
    user_email: str,
    user_name: str,
    title: str,
    body: str,
    metadata: dict[str, Any],
) -> None:
    """
    Send an email for notification types that require it (follow, reaction).

    Silently skips for other types or when SendGrid is not configured.
    """
    if notification_type not in EMAIL_NOTIFICATION_TYPES:
        return

    if notification_type == "follow":
        html = _build_html(
            title=title,
            body=body,
            cta_text="View Profile",
            cta_url=metadata.get("profile_url", "https://app.zylvex.io"),
        )
    elif notification_type == "reaction":
        html = _build_html(
            title=title,
            body=body,
            cta_text="See Reactions",
            cta_url=metadata.get("content_url", "https://app.zylvex.io"),
        )
    else:
        html = _build_html(title=title, body=body)

    await send_email(
        to_email=user_email,
        to_name=user_name,
        subject=title,
        html_content=html,
    )
