import json

import requests
from data import active_agent_triggers_params, icmp_triggers_params


def create_triggers():
    url = "http://4.233.79.31:8080/api_jsonrpc.php"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 98822a8062620e621d93240ce8ad0be8",
    }
    body = {
        "jsonrpc": "2.0",
        "method": "trigger.create",
        "params": active_agent_triggers_params,
        "id": 1,
    }

    print("Sending request...")

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        try:
            data = response.json()

            if "error" in data:
                print("🚨 API Error Returned:")
                print(data["error"])
                return None

            result_items = data.get("result")
            if not result_items:
                print("⚠️ No result found in response.")
                return None

            print("✅ Trigger(s) created successfully.")
            return data

        except json.JSONDecodeError as e:
            print(f"❌ Failed to decode JSON: {e}")
            print("Raw Response Text:", response.text[:500])
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


create_triggers()
