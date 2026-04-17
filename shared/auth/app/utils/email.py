"""
Email utilities for the auth service.

Sends verification and password reset emails via SendGrid.
Falls back to console logging when SENDGRID_API_KEY is not set.
"""

import logging
import os

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@zylvex.io")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Zylvex")


def _build_html(title: str, body: str, cta_text: str, cta_url: str) -> str:
    """Render a dark-themed, Zylvex branded HTML email."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#1B2A4A;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#1B2A4A;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#0f1b33;border-radius:16px;
                      border:1px solid rgba(255,255,255,0.08);
                      overflow:hidden;max-width:560px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1B2A4A,#2a3f6a);
                       padding:32px 40px;text-align:center;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#6C63FF,#8b7aff);
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
              <div style="text-align:center;margin:32px 0;">
                <a href="{cta_url}"
                   style="background:linear-gradient(135deg,#6C63FF,#8b7aff);
                          color:#fff;text-decoration:none;padding:14px 32px;
                          border-radius:8px;font-weight:600;font-size:15px;
                          display:inline-block;">
                  {cta_text}
                </a>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#0a1526;padding:20px 40px;
                       border-top:1px solid rgba(255,255,255,0.06);">
              <p style="color:#475569;font-size:12px;margin:0;text-align:center;">
                You received this email from
                <a href="https://zylvex.io"
                   style="color:#6C63FF;text-decoration:none;">Zylvex Technologies</a>.
                <br />If you didn't request this, you can safely ignore it.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _send_via_sendgrid(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via SendGrid API. Returns True on success."""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        message = Mail(
            from_email=Email(EMAIL_FROM, EMAIL_FROM_NAME),
            to_emails=To(to_email),
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


def _send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email via SendGrid if configured, otherwise log to console (dev mode).
    """
    if not SENDGRID_API_KEY:
        logger.info(
            "[DEV MODE] Email not sent (SENDGRID_API_KEY not set).\n"
            "  To: %s\n  Subject: %s\n  Body preview: %s...",
            to_email,
            subject,
            html_content[:200],
        )
        return False
    return _send_via_sendgrid(to_email, subject, html_content)


def send_verification_email(
    to_email: str, token: str, frontend_url: str
) -> bool:
    """Send email verification link to user."""
    verification_url = f"{frontend_url}/verify-email?token={token}"
    subject = "Verify your Zylvex account"
    body = (
        "Welcome to Zylvex! Please verify your email address to get started. "
        "Click the button below to confirm your account. "
        "This link will expire in 24 hours."
    )
    html = _build_html(
        title=subject,
        body=body,
        cta_text="Verify Email",
        cta_url=verification_url,
    )
    return _send_email(to_email, subject, html)


def send_password_reset_email(
    to_email: str, token: str, frontend_url: str
) -> bool:
    """Send password reset link to user."""
    reset_url = f"{frontend_url}/reset-password?token={token}"
    subject = "Reset your Zylvex password"
    body = (
        "We received a request to reset your password. "
        "Click the button below to set a new password. "
        "This link will expire in 1 hour. "
        "If you didn't request this, you can safely ignore this email."
    )
    html = _build_html(
        title=subject,
        body=body,
        cta_text="Reset Password",
        cta_url=reset_url,
    )
    return _send_email(to_email, subject, html)
