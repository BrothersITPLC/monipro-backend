import logging
import os

import requests
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# from utils import ServiceErrorHandler


load_dotenv(override=True)

payment_logger = logging.getLogger("payment")


TELEBIRR_TOKEN_PATH = os.getenv("TELEBIRR_TOKEN_PATH")
TELEBIRR_BASE_URL = os.getenv("TELEBIRR_BASE_URL")
TELEBIRR_APP_ID = os.getenv("TELEBIRR_APP_ID")
TELEBIRR_APP_SECRET = os.getenv("TELEBIRR_APP_SECRET")


def telebirr_apply_fabric_token():
    """
    Call /payment/v1/token to get a Fabric token. Raises on HTTP error.
    Returns the requests.Response object.
    """
    missing_vars = []
    if not TELEBIRR_TOKEN_PATH:
        missing_vars.append("TELEBIRR_TOKEN_PATH")
    if not TELEBIRR_BASE_URL:
        missing_vars.append("TELEBIRR_BASE_URL")
    if not TELEBIRR_APP_ID:
        missing_vars.append("TELEBIRR_APP_ID")
    if not TELEBIRR_APP_SECRET:
        missing_vars.append("TELEBIRR_APP_SECRET")
    if missing_vars:
        error_msg = f"{', '.join(missing_vars)} is not set in environment variables."
        payment_logger.error(error_msg)
        # raise ServiceErrorHandler("Something went wrong, please try again later.")

    url = TELEBIRR_BASE_URL + TELEBIRR_TOKEN_PATH
    headers = {
        "Content-Type": "application/json",
        "X-APP-Key": TELEBIRR_APP_ID,
    }
    body = {"appSecret": TELEBIRR_APP_SECRET}

    try:
        response = requests.post(
            url, json=body, headers=headers, verify=False, timeout=10
        )
        response.raise_for_status()
        response_object = response.json()

        return response_object

    except requests.exceptions.JSONDecodeError as e:
        payment_logger.error(
            f"Failed to decode JSON from response: {e}. Raw response: {response.text}"
        )
        # raise ServiceErrorHandler("Something went wrong, please try again later.")
    except requests.exceptions.SSLError as e:
        payment_logger.error(f"SSL Error occurred: {e}")
        # raise ServiceErrorHandler("Something went wrong, please try again later.")
    except requests.exceptions.ConnectionError as e:
        payment_logger.error(f"Connection Error occurred: {e}")
        # raise ServiceErrorHandler("Something went wrong, please try again later.")
    except requests.exceptions.Timeout as e:
        payment_logger.error(f"Request timed out: {e}")
        # raise ServiceErrorHandler("Something went wrong, please try again later.")
    except requests.exceptions.HTTPError as e:
        payment_logger.error(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
        # raise ServiceErrorHandler("Something went wrong, please try again later.")
    except requests.exceptions.RequestException as e:
        payment_logger.error(f"An error occurred during the request: {e}")
        # raise ServiceErrorHandler("Something went wrong, please try again later.")
