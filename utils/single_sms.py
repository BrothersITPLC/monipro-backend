# # we use requests library for the samples
# import requests

# # session object
# session = requests.Session()
# # base url
# base_url = "https://api.afromessage.com/api/send"
# # api token
# token = "eyJhbGciOiJIUzI1NiJ9.eyJpZGVudGlmaWVyIjoiQlJ6OWNnYlZWTjZUMFNlZkRRYmNwY1Y0MTJrSHJ2QVgiLCJleHAiOjE5MDU1MDAyMzAsImlhdCI6MTc0NzczMzgzMCwianRpIjoiOWY1M2JhMTQtZjlkNC00ODU5LWFhNzUtZmYzNWQzODIyMTZlIn0.x03JkZ6DxcfDbJqTXBS23Gvyv-8VDedgS6YkWWlgsLI"
# # header
# headers = {"Authorization": "Bearer " + token}
# # request body
# body = {"to": "+251965917665", "message": "kid gegema"}
# # make request
# result = session.post(base_url, json=body, headers=headers)
# # check result
# if result.status_code == 200:
#     # request is success. inspect the json object for the value of `acknowledge`
#     json = result.json()
#     print(json)
#     if json["acknowledge"] == "success":
#         # do success
#         print("api success")
#     else:
#         # do failure
#         print("api error")
# else:
#     # anything other than 200 goes here.
#     print("http error ... code: %d , msg: %s " % (result.status_code, result.content))

import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
sms_logger = logging.getLogger("sms")
AFRO_MESSAGE_TOKEN = os.getenv("AFRO_MESSAGE_TOKEN")
AFRO_MESSAGE_TOKEN_NEW = os.getenv("AFRO_MESSAGE_TOKEN_NEW")
AFRO_MESSAGE_URL = os.getenv("AFRO_MESSAGE_URL")


def send_single_sms(to, message):
    session = requests.Session()
    headers = {"Authorization": f"Bearer {AFRO_MESSAGE_TOKEN_NEW}"}
    payload = {"to": to, "message": message}
    print(payload)

    try:
        result = session.post(AFRO_MESSAGE_URL, json=payload, headers=headers)
        sms_logger.debug(f"HTTP {result.status_code} — Response body: {result.text}")

        result.raise_for_status()

        response_json = result.json()
        sms_logger.debug(f"Parsed JSON: {response_json}")

        if response_json.get("acknowledge") == "success":
            msg_id = response_json.get("response", {}).get("message_id", "")
            sms_logger.info(f"SMS sent successfully to {to}, message_id={msg_id}")
            return {
                "status": "success",
                "message": "SMS sent successfully",
                "data": msg_id,
            }
        else:
            err = response_json.get("error") or response_json.get("response", {}).get(
                "errors"
            )
            sms_logger.error(f"Failed to send SMS to {to}. Error: {err}")
            return {"status": "error", "message": "Failed to send SMS", "data": err}

    except requests.HTTPError as http_err:
        sms_logger.error(f"HTTP error during request: {http_err}")
        return {"status": "error", "message": "HTTP error", "data": ""}
    except ValueError as json_err:
        sms_logger.error(f"Invalid JSON in response: {json_err}")
        return {"status": "error", "message": "Invalid JSON", "data": ""}
    except Exception as e:
        sms_logger.error(f"Unexpected error: {e}")
        return {"status": "error", "message": "Unknown error", "data": ""}
