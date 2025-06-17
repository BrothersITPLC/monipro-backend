import json
import logging
import os

import requests
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from payment.functions.telebirr_apply_fabric_token import telebirr_apply_fabric_token
from payment.functions.telebirr_utils import (
    current_timestamp,
    flatten_and_sign,
    order_id,
    random_nonce_str,
)

load_dotenv(override=True)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if not logging.getLogger("payment").hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
payment_logger = logging.getLogger("payment")

TELEBIRR_BASE_URL = os.getenv("TELEBIRR_BASE_URL")
TELEBIRR_APP_ID = os.getenv("TELEBIRR_APP_ID")
TELEBIRR_PREORDER_PATH = os.getenv("TELEBIRR_PREORDER_PATH")
TELEBIRR_MERCHANT_CODE = os.getenv("TELEBIRR_MERCHANT_CODE")
CHAPA_REDIRECT_URL = os.getenv("CHAPA_REDIRECT_URL")
TELEBIRR_PRIVATE_KEY = os.getenv("TELEBIRR_PRIVATE_KEY")
TELEBIRR_MERCHANT_APP_ID = os.getenv("TELEBIRR_MERCHANT_APP_ID")


def create_preorder(title: str, amount: str, fabric_token: str):
    """
    Call /payment/v1/merchant/preOrder with the required biz_content fields.
    Returns the JSON response from telebirr.
    """
    missing = []
    for var_name in [
        "TELEBIRR_BASE_URL",
        "TELEBIRR_APP_ID",
        "TELEBIRR_PREORDER_PATH",
        "TELEBIRR_MERCHANT_CODE",
        "TELEBIRR_MERCHANT_APP_ID",
        "TELEBIRR_PRIVATE_KEY",
    ]:
        if not globals().get(var_name):
            missing.append(var_name)
    if not fabric_token:
        missing.append("fabric_token (dynamic)")

    if missing:
        err = f"Missing environment variables: {', '.join(missing)}"
        payment_logger.error(err)
        raise ValueError(err)

    base_url = TELEBIRR_BASE_URL
    preorder_path = TELEBIRR_PREORDER_PATH
    url = base_url + preorder_path

    headers = {
        "Content-Type": "application/json",
        "X-APP-Key": TELEBIRR_APP_ID,
        "Authorization": fabric_token,
    }

    # Generate a new order ID
    current_merch_order_id = order_id()
    redirect_full = f"{CHAPA_REDIRECT_URL}/{current_merch_order_id}/"

    # Construct biz_content exactly as Telebirr expects
    payment_logger.debug(f"MERCHANT_APP_ID (repr): {repr(TELEBIRR_MERCHANT_APP_ID)}")
    payment_logger.debug(f"MERCHANT_CODE   (repr): {repr(TELEBIRR_MERCHANT_CODE)}")
    payment_logger.debug(f"PRIVATE_KEY     (repr): {repr(TELEBIRR_PRIVATE_KEY)[:30]}…")
    payment_logger.debug(f"REDIRECT_URL    (repr): {repr(redirect_full)}")

    biz_content = {
        "trade_type": "Checkout",
        "appid": TELEBIRR_MERCHANT_APP_ID,
        "merch_code": TELEBIRR_MERCHANT_CODE,
        "merch_order_id": current_merch_order_id,
        "title": title,
        "total_amount": amount,
        "trans_currency": "ETB",
        "timeout_express": "120m",
        "notify_url": "https://monipro.brothersid.dev/payment/callback",
        "redirect_url": redirect_full,
        # "payee_identifier": TELEBIRR_MERCHANT_CODE,
        # "payee_identifier_type": "04",
        # "payee_type": "3000",
        # "business_type": "BuyGoods",
    }

    # Build the top-level JSON exactly as Telebirr wants
    payload_obj = {
        "timestamp": current_timestamp(),  # must be 10 digits, UTC seconds
        "nonce_str": random_nonce_str(32),
        "method": "payment.preorder",
        "version": "1.0",
        "biz_content": biz_content,
    }

    # Compute the signature over all flattened fields
    signature = flatten_and_sign(payload_obj, TELEBIRR_PRIVATE_KEY)
    payload_obj["sign"] = signature
    payload_obj["sign_type"] = "SHA256WithRSA"

    # Debug: log the full request JSON
    payment_logger.debug(f"Request to TELEBIRR:\n{json.dumps(payload_obj, indent=2)}")

    # Send the POST
    resp = requests.post(
        url, json=payload_obj, headers=headers, verify=False, timeout=15
    )
    payment_logger.info(f"Preorder Status: {resp.status_code}")
    payment_logger.info(f"Preorder Response: {resp.text}")
    resp.raise_for_status()
    return resp.json()


# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     )
#     tpl_logger = logging.getLogger("payment")
#     tpl_logger.info("--- Starting Telebirr Preorder Test ---")

#     env_fabric = telebirr_apply_fabric_token()
#     token = env_fabric.get("token") if env_fabric else None
#     tpl_logger.info(f"Dynamic Fabric Token: {token}")

#     if not token:
#         tpl_logger.error("Could not retrieve a fabric token; aborting.")
#     else:
#         try:
#             tpl_logger.info("Calling create_preorder …")
#             resp_json = create_preorder(
#                 title="Test Product", amount="1.00", fabric_token=token
#             )
#             tpl_logger.info(
#                 f"Preorder SUCCESS! Response JSON:\n{json.dumps(resp_json, indent=2)}"
#             )
#         except Exception as e:
#             tpl_logger.error(f"Preorder failed: {e}", exc_info=True)

#     tpl_logger.info("--- Finished Telebirr Preorder Test ---")
