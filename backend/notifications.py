"""
Notification System for RAIA Enterprise
========================================

Provides multi-channel notifications:
- Email notifications
- Slack notifications
- Webhook notifications
- In-app notifications
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiohttp
import json
from pydantic import BaseModel, EmailStr

# ============================================================================
# Models
# ============================================================================

class NotificationLevel(str, Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class Notification(BaseModel):
    """Notification model."""
    id: str
    level: NotificationLevel
    title: str
    message: str
    channels: List[NotificationChannel]
    recipients: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()
    sent: bool = False


# ============================================================================
# Email Notifications
# ============================================================================

class EmailConfig(BaseModel):
    """Email configuration."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    from_email: EmailStr
    from_name: str = "RAIA Enterprise"
    use_tls: bool = True


class EmailNotifier:
    """Send email notifications."""

    def __init__(self, config: EmailConfig):
        """
        Initialize email notifier.

        Args:
            config: Email configuration
        """
        self.config = config

    def send(
        self,
        to: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email notification.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            attachments: Optional list of file paths to attach

        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject

            # Add text body
            msg.attach(MIMEText(body, 'plain'))

            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)

            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()

                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)

            print(f"✅ Email sent to {', '.join(to)}")
            return True

        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False

    def send_alert(
        self,
        to: List[str],
        level: NotificationLevel,
        title: str,
        message: str,
        details: Optional[Dict] = None
    ) -> bool:
        """
        Send alert email.

        Args:
            to: Recipients
            level: Alert level
            title: Alert title
            message: Alert message
            details: Optional details

        Returns:
            True if sent successfully
        """
        # Determine emoji and color based on level
        emoji_map = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨"
        }

        color_map = {
            NotificationLevel.INFO: "#0066cc",
            NotificationLevel.WARNING: "#ff9900",
            NotificationLevel.ERROR: "#cc0000",
            NotificationLevel.CRITICAL: "#990000"
        }

        emoji = emoji_map.get(level, "📢")
        color = color_map.get(level, "#666666")

        # Plain text body
        body = f"""
{emoji} {level.upper()} ALERT

{title}

{message}

{'-' * 50}
Time: {datetime.utcnow().isoformat()}
Level: {level}
"""

        if details:
            body += "\nDetails:\n"
            for key, value in details.items():
                body += f"  {key}: {value}\n"

        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color};">{emoji} {title}</h2>
                <p style="font-size: 14px; color: #333;">{message}</p>

                <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <p style="margin: 5px 0;"><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    <p style="margin: 5px 0;"><strong>Level:</strong> <span style="color: {color}; font-weight: bold;">{level.upper()}</span></p>
                </div>
        """

        if details:
            html_body += """
                <div style="margin-top: 20px;">
                    <h3 style="color: #333;">Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
            """
            for key, value in details.items():
                html_body += f"""
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">{key}</td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{value}</td>
                        </tr>
                """
            html_body += """
                    </table>
                </div>
            """

        html_body += """
            </div>
            <p style="margin-top: 30px; font-size: 12px; color: #999;">
                This is an automated notification from RAIA Enterprise.
            </p>
        </body>
        </html>
        """

        return self.send(
            to=to,
            subject=f"[RAIA {level.upper()}] {title}",
            body=body,
            html_body=html_body
        )


# ============================================================================
# Slack Notifications
# ============================================================================

class SlackNotifier:
    """Send Slack notifications."""

    def __init__(self, webhook_url: str):
        """
        Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url

    async def send(
        self,
        message: str,
        channel: Optional[str] = None,
        username: Optional[str] = "RAIA Bot",
        icon_emoji: Optional[str] = ":robot_face:"
    ) -> bool:
        """
        Send Slack message.

        Args:
            message: Message text
            channel: Optional channel override
            username: Bot username
            icon_emoji: Bot icon

        Returns:
            True if sent successfully
        """
        payload = {
            "text": message,
            "username": username,
            "icon_emoji": icon_emoji
        }

        if channel:
            payload["channel"] = channel

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        print(f"✅ Slack message sent")
                        return True
                    else:
                        print(f"❌ Slack sending failed: {response.status}")
                        return False

        except Exception as e:
            print(f"❌ Slack sending failed: {e}")
            return False

    async def send_alert(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        details: Optional[Dict] = None
    ) -> bool:
        """
        Send alert to Slack.

        Args:
            level: Alert level
            title: Alert title
            message: Alert message
            details: Optional details

        Returns:
            True if sent successfully
        """
        # Color based on level
        color_map = {
            NotificationLevel.INFO: "#0066cc",
            NotificationLevel.WARNING: "#ff9900",
            NotificationLevel.ERROR: "#cc0000",
            NotificationLevel.CRITICAL: "#990000"
        }

        emoji_map = {
            NotificationLevel.INFO: ":information_source:",
            NotificationLevel.WARNING: ":warning:",
            NotificationLevel.ERROR: ":x:",
            NotificationLevel.CRITICAL: ":rotating_light:"
        }

        color = color_map.get(level, "#666666")
        emoji = emoji_map.get(level, ":bell:")

        # Build attachment
        attachment = {
            "color": color,
            "title": f"{emoji} {title}",
            "text": message,
            "fields": [
                {
                    "title": "Level",
                    "value": level.upper(),
                    "short": True
                },
                {
                    "title": "Time",
                    "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                    "short": True
                }
            ],
            "footer": "RAIA Enterprise",
            "ts": int(datetime.utcnow().timestamp())
        }

        if details:
            for key, value in details.items():
                attachment["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })

        payload = {
            "attachments": [attachment],
            "username": "RAIA Alert Bot",
            "icon_emoji": emoji
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 200

        except Exception as e:
            print(f"❌ Slack alert failed: {e}")
            return False


# ============================================================================
# Webhook Notifications
# ============================================================================

class WebhookNotifier:
    """Send webhook notifications."""

    def __init__(self, webhook_url: str, auth_token: Optional[str] = None):
        """
        Initialize webhook notifier.

        Args:
            webhook_url: Webhook URL
            auth_token: Optional authentication token
        """
        self.webhook_url = webhook_url
        self.auth_token = auth_token

    async def send(self, payload: Dict) -> bool:
        """
        Send webhook notification.

        Args:
            payload: Data to send

        Returns:
            True if sent successfully
        """
        headers = {"Content-Type": "application/json"}

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status in [200, 201, 202]:
                        print(f"✅ Webhook sent to {self.webhook_url}")
                        return True
                    else:
                        print(f"❌ Webhook failed: {response.status}")
                        return False

        except Exception as e:
            print(f"❌ Webhook failed: {e}")
            return False


# ============================================================================
# Notification Manager
# ============================================================================

class NotificationManager:
    """Unified notification manager."""

    def __init__(
        self,
        email_config: Optional[EmailConfig] = None,
        slack_webhook: Optional[str] = None,
        webhook_url: Optional[str] = None
    ):
        """
        Initialize notification manager.

        Args:
            email_config: Email configuration
            slack_webhook: Slack webhook URL
            webhook_url: Custom webhook URL
        """
        self.email_notifier = EmailNotifier(email_config) if email_config else None
        self.slack_notifier = SlackNotifier(slack_webhook) if slack_webhook else None
        self.webhook_notifier = WebhookNotifier(webhook_url) if webhook_url else None

        # In-app notifications (stored in memory, should use DB in production)
        self.in_app_notifications: List[Notification] = []

    async def send_notification(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        channels: List[NotificationChannel],
        recipients: Optional[List[str]] = None,
        details: Optional[Dict] = None
    ) -> Dict[str, bool]:
        """
        Send notification through multiple channels.

        Args:
            level: Notification level
            title: Notification title
            message: Notification message
            channels: Channels to send through
            recipients: Recipients (for email)
            details: Additional details

        Returns:
            Dict of channel: success status
        """
        results = {}

        # Email
        if NotificationChannel.EMAIL in channels and self.email_notifier and recipients:
            results[NotificationChannel.EMAIL] = self.email_notifier.send_alert(
                to=recipients,
                level=level,
                title=title,
                message=message,
                details=details
            )

        # Slack
        if NotificationChannel.SLACK in channels and self.slack_notifier:
            results[NotificationChannel.SLACK] = await self.slack_notifier.send_alert(
                level=level,
                title=title,
                message=message,
                details=details
            )

        # Webhook
        if NotificationChannel.WEBHOOK in channels and self.webhook_notifier:
            payload = {
                "level": level,
                "title": title,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
            results[NotificationChannel.WEBHOOK] = await self.webhook_notifier.send(payload)

        # In-app
        if NotificationChannel.IN_APP in channels:
            notification = Notification(
                id=str(datetime.utcnow().timestamp()),
                level=level,
                title=title,
                message=message,
                channels=channels,
                recipients=recipients or [],
                metadata=details or {},
                sent=True
            )
            self.in_app_notifications.append(notification)
            results[NotificationChannel.IN_APP] = True

        return results

    def get_in_app_notifications(
        self,
        user_id: Optional[str] = None,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get in-app notifications.

        Args:
            user_id: Filter by user
            unread_only: Only unread notifications

        Returns:
            List of notifications
        """
        notifications = self.in_app_notifications

        if user_id:
            notifications = [
                n for n in notifications
                if user_id in n.recipients or not n.recipients
            ]

        # Sort by created_at descending
        notifications.sort(key=lambda x: x.created_at, reverse=True)

        return notifications


# ============================================================================
# Alert Templates
# ============================================================================

class AlertTemplates:
    """Pre-defined alert templates."""

    @staticmethod
    async def drift_detected(
        notifier: NotificationManager,
        run_id: str,
        drift_score: float,
        threshold: float
    ):
        """Alert for drift detection."""
        await notifier.send_notification(
            level=NotificationLevel.WARNING,
            title="Embedding Drift Detected",
            message=f"Drift detected in run {run_id}",
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.IN_APP],
            recipients=["admin@example.com"],
            details={
                "run_id": run_id,
                "drift_score": drift_score,
                "threshold": threshold,
                "status": "requires_attention"
            }
        )

    @staticmethod
    async def quality_degradation(
        notifier: NotificationManager,
        metric: str,
        current_value: float,
        expected_value: float
    ):
        """Alert for quality degradation."""
        await notifier.send_notification(
            level=NotificationLevel.ERROR,
            title="Quality Degradation Detected",
            message=f"Metric '{metric}' has degraded below expected threshold",
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            recipients=["ops@example.com"],
            details={
                "metric": metric,
                "current_value": current_value,
                "expected_value": expected_value,
                "degradation": f"{((expected_value - current_value) / expected_value * 100):.1f}%"
            }
        )

    @staticmethod
    async def system_error(
        notifier: NotificationManager,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ):
        """Alert for system errors."""
        await notifier.send_notification(
            level=NotificationLevel.CRITICAL,
            title="System Error",
            message=f"Critical error: {error_type}",
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
            recipients=["devops@example.com"],
            details={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace or "N/A"
            }
        )


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test():
        # Configure email
        email_config = EmailConfig(
            smtp_username="your-email@gmail.com",
            smtp_password="your-app-password",
            from_email="noreply@raia.com"
        )

        # Initialize manager
        manager = NotificationManager(
            email_config=email_config,
            slack_webhook="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        )

        # Send test notification
        results = await manager.send_notification(
            level=NotificationLevel.INFO,
            title="Test Notification",
            message="This is a test notification from RAIA",
            channels=[NotificationChannel.IN_APP],
            details={"test": "value"}
        )

        print(f"Notification results: {results}")

        # Use alert template
        await AlertTemplates.drift_detected(
            manager,
            run_id="run_123",
            drift_score=0.85,
            threshold=0.70
        )

    asyncio.run(test())
