import os
import requests
from datetime import datetime, timezone
from flask import current_app
from app.extensions import db
from app.models.notification import Notification, NotificationStatus, NotificationChannel

def send_resend_email(to_email: str, subject: str, html_body: str, notification_type: str, user_id: str, profile_id: str = None) -> Notification:
    """
    Sends an email using Resend API and records the delivery attempt in the database.
    Strictly reports delivery status: if API key is not configured, records SIMULATED_NOT_CONFIGURED.
    """
    api_key = current_app.config.get("RESEND_API_KEY", "")
    mail_from = current_app.config.get("MAIL_FROM", "ElderCare <onboarding@resend.dev>")

    notification = Notification(
        user_id=user_id,
        profile_id=profile_id,
        type=notification_type,
        channel=NotificationChannel.EMAIL,
        title=subject,
        message=html_body,
        recipient_email=to_email,
        status=NotificationStatus.QUEUED,
        delivery_attempts=1
    )
    db.session.add(notification)
    db.session.flush()

    # Verify if Resend API key is configured
    if not api_key or api_key == "re_your_api_key_here" or not api_key.startswith("re_"):
        notification.status = NotificationStatus.SIMULATED_NOT_CONFIGURED
        notification.error_message = (
            "Resend API key not configured. Set RESEND_API_KEY in environment variables or .env file to dispatch real emails."
        )
        db.session.commit()
        return notification

    # Real dispatch via Resend REST API
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": mail_from,
                "to": [to_email],
                "subject": subject,
                "html": html_body
            },
            timeout=10
        )
        if response.status_code in [200, 201]:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            notification.error_message = None
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = f"Resend API Error ({response.status_code}): {response.text}"
    except Exception as e:
        notification.status = NotificationStatus.FAILED
        notification.error_message = f"Network or dispatch error: {str(e)}"

    db.session.commit()
    return notification


# --- Email HTML Templates (Clean, high-contrast, healthcare styled) ---

def render_email_template(header_title: str, greeting: str, main_content_html: str, action_button_text: str = None, action_button_url: str = None) -> str:
    btn_html = ""
    if action_button_text and action_button_url:
        btn_html = f"""
        <div style="margin-top: 28px; text-align: center;">
            <a href="{action_button_url}" style="background-color: #2563eb; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block;">
                {action_button_text}
            </a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{header_title}</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
            <tr>
                <td style="background: linear-gradient(135deg, #1e40af, #3b82f6); padding: 24px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: -0.5px;">ElderCare Platform</h1>
                    <p style="color: #e0e7ff; margin: 6px 0 0 0; font-size: 14px;">Smart Healthcare & Medication Management</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 32px 28px;">
                    <h2 style="color: #0f172a; margin-top: 0; font-size: 20px;">{greeting}</h2>
                    <div style="font-size: 16px; line-height: 1.6; color: #334155;">
                        {main_content_html}
                    </div>
                    {btn_html}
                </td>
            </tr>
            <tr>
                <td style="background-color: #f1f5f9; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b;">
                    <p style="margin: 0;">This is an automated notification from ElderCare. Please do not reply directly to this email.</p>
                    <p style="margin: 6px 0 0 0;">Ensuring dignified, reliable, and connected healthcare for our loved ones.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
