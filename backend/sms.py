import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_sms(message, phone=None):
    """Generic SMS adapter.

    Configure your chosen SMS provider's endpoint and authentication.
    The provider-specific payload must be implemented here.
    """
    provider_url = os.getenv("SMS_PROVIDER_URL")
    api_key = os.getenv("SMS_API_KEY")
    phone = phone or os.getenv("ALERT_PHONE_NUMBER")

    if not provider_url or not api_key or not phone:
        return {"sent": False, "message": "SMS credentials/provider not configured."}

    # Replace payload/headers with your provider's official API format.
    response = requests.post(
        provider_url,
        json={"to": phone, "message": message},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    response.raise_for_status()
    return {"sent": True}
