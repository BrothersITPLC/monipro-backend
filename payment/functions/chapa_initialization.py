# payment/functions.py

import decimal
import logging
import os

import requests
from dotenv import load_dotenv

from utils import ServiceErrorHandler

load_dotenv()

payment_logger = logging.getLogger("payment")
CHAPA_SECRET = os.getenv("CHAPA_SECRET")
CHAPA_API_URL = os.getenv("CHAPA_API_URL")
CHAPA_API_VERSION = os.getenv("CHAPA_API_VERSION")


def decimal_to_float(obj):
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj


def initialize_chapa_payment(chapa_payload):
    """
    Calls Chapa's /transaction/initialize endpoint.
    Raises ServiceErrorHandler on any failure.
    Returns the parsed JSON dict on success.
    """
    if not (CHAPA_SECRET and CHAPA_API_URL and CHAPA_API_VERSION):
        raise ServiceErrorHandler("Payment gateway is not configured properly.")

    url = f"{CHAPA_API_URL}/{CHAPA_API_VERSION}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET}",
        "Content-Type": "application/json",
    }
    try:
        safe_payload = decimal_to_float(chapa_payload)

        resp = requests.post(url, headers=headers, json=safe_payload, timeout=10)
    except requests.RequestException as e:
        payment_logger.error(f"Chapa connection error: {e}")
        raise ServiceErrorHandler("Unable to reach payment gateway, please try again.")

    try:
        data = resp.json()
    except ValueError:
        payment_logger.error("Chapa response not JSON")
        raise ServiceErrorHandler("Invalid response from payment gateway.")

    if resp.status_code != 200 or data.get("status") != "success":
        payment_logger.error(
            f"Chapa API error ({resp.status_code}): {data.get('message', data)}"
        )
        raise ServiceErrorHandler(data.get("message", "Payment initialization failed."))

    return data
