"""SMS provider integration.

The project deliberately uses a small adapter instead of hard-coding a
specific vendor SDK. Configure the official provider endpoint and credentials
through environment variables and adjust the payload/header format if needed.
"""

from __future__ import annotations

import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class SMSProviderError(RuntimeError):
    """Raised when an SMS provider request fails."""


def send_sms(message: str, phone: Optional[str] = None) -> dict:
    provider_url = os.getenv("SMS_PROVIDER_URL")
    api_key = os.getenv("SMS_API_KEY")
    target_phone = phone or os.getenv("ALERT_PHONE_NUMBER")

    if not provider_url or not api_key or not target_phone:
        return {
            "sent": False,
            "message": "SMS provider not configured",
        }

    # This is a generic JSON adapter. The exact payload/header format must
    # match the official API documentation of the provider selected by the team.
    try:
        response = requests.post(
            provider_url,
            json={"to": target_phone, "message": message},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SMSProviderError("SMS provider request failed.") from exc

    return {"sent": True, "phone": target_phone}
