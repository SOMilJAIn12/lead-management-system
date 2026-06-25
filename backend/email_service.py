"""
email_service.py
-----------------
Sends the personalized "Thank You For Contacting Us" email via Gmail SMTP.

The email contains:
  - A personalized greeting and the lead's own requirement text quoted back
  - A "learn more" link that routes through GET /click/{lead_id} (link click
    tracking) before redirecting to the final destination
  - A hidden 1x1 tracking pixel pointing at GET /open/{lead_id} (email open
    tracking)

All credentials are read from environment variables - nothing is hardcoded.
If credentials are missing, sending is skipped gracefully (the app keeps
working, the lead is still saved, `email_sent` just stays False).
"""
import os
import smtplib
import logging
from typing import Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("email_service")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))


def build_email_body(full_name: str, requirement: str, lead_id: str) -> Tuple[str, str]:
    """Build (plain_text, html) bodies for the lead's thank-you email."""
    click_url = f"{BASE_URL}/click/{lead_id}"
    pixel_url = f"{BASE_URL}/open/{lead_id}"

    plain_text = (
        f"Hi {full_name},\n\n"
        f"Thank you for reaching out.\n\n"
        f"We received your requirement:\n"
        f"\"{requirement}\"\n\n"
        f"You can learn more here:\n{click_url}\n\n"
        f"Regards,\nLead Management Team"
    )

    html = f"""\
    <html>
      <body style="font-family: Arial, Helvetica, sans-serif; color: #1f2937; line-height: 1.6; max-width: 560px;">
        <p>Hi {full_name},</p>
        <p>Thank you for reaching out.</p>
        <p>We received your requirement:</p>
        <p style="padding: 12px 16px; background:#f3f4f6; border-left: 4px solid #4f46e5; margin: 0 0 16px 0;">
          "{requirement}"
        </p>
        <p>
          You can learn more here:<br/>
          <a href="{click_url}" style="color:#4f46e5;">{click_url}</a>
        </p>
        <p>Regards,<br/>Lead Management Team</p>
        <!-- Hidden tracking pixel: loading this image marks the email as opened -->
        <img src="{pixel_url}" width="1" height="1" style="display:none;" alt="" />
      </body>
    </html>
    """
    return plain_text, html


def send_lead_email(full_name: str, to_email: str, requirement: str, lead_id: str) -> bool:
    """
    Send the personalized thank-you email to the lead.
    Returns True if the email was sent successfully, False otherwise.
    Never raises - failures are logged and swallowed so a flaky SMTP server
    never breaks lead capture.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.warning(
            "GMAIL_USER / GMAIL_APP_PASSWORD not configured in .env - "
            "skipping email send. The lead was still saved."
        )
        return False

    plain_text, html = build_email_body(full_name, requirement, lead_id)

    message = MIMEMultipart("alternative")
    message["Subject"] = "Thank You For Contacting Us"
    message["From"] = GMAIL_USER
    message["To"] = to_email

    # Attach plain text first, HTML second (clients prefer the last part that
    # they can render, per the MIME multipart/alternative convention).
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, message.as_string())
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
