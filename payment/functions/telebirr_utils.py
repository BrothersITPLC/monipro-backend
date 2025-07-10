import logging
import random
import string
import time
from base64 import b64decode, b64encode

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss

payment_logger = logging.getLogger("payment")


payment_logger = logging.getLogger("payment")


def current_timestamp():
    """Returns the current UTC timestamp in seconds as a string."""
    return str(int(time.time()))


def order_id():
    """Generates a unique order ID (example: timestamp + random string)."""
    return current_timestamp() + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=10)
    )


def current_timestamp():
    """Return a 10-digit UTC timestamp string (seconds)."""
    return str(int(time.time()))


def random_nonce_str(length=32):
    """Return a 32-char random alphanumeric string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def SignWithRSA(data_str: str, private_key_b64: str) -> str:
    """
    Perform SHA256withRSA (PSS, salt_length=32) on `data_str` and return base64 signature.
    """
    # Decode the raw base64 key into bytes, then import via PyCrypto
    key_bytes = b64decode(private_key_b64.encode("utf-8"))
    rsa_key = RSA.import_key(key_bytes)

    # Compute SHA256 digest
    digest = SHA256.new()
    digest.update(data_str.encode("utf-8"))

    # Sign using PSS with salt_length=32 (exactly the digest length of SHA256)
    signer = pss.new(rsa_key, salt_bytes=32)
    signature_bytes = signer.sign(digest)

    # Base64-encode with no line breaks
    return b64encode(signature_bytes).decode("utf-8")


def flatten_and_sign(payload_obj: dict, private_key_b64: str) -> str:
    """
    Flatten all keys (except sign/sign_type), including biz_content sub-keys,
    sort lexicographically, join with '&', and PSS-sign.
    """
    exclude = {"sign", "sign_type", "header", "refund_info", "openType", "raw_request"}
    kv_list = []

    for key, val in payload_obj.items():
        if key in exclude:
            continue
        if key == "biz_content":
            # biz_content is itself a dict: flatten those keys
            for subk, subv in payload_obj["biz_content"].items():
                kv_list.append(f"{subk}={subv}")
        else:
            # top-level keys (timestamp, nonce_str, method, version)
            kv_list.append(f"{key}={val}")

    # Sort lexicographically by the entire "k=v" string (i.e. by key name first)
    kv_list.sort()
    data_to_sign = "&".join(kv_list)

    # Debug: log the exact string you’re signing
    payment_logger.debug(f"STRING_TO_BE_SIGNED:\n<{data_to_sign}>\n--end--")

    # Now sign with RSA+PSS+SHA256 (salt_length=32)
    return SignWithRSA(data_to_sign, private_key_b64)
