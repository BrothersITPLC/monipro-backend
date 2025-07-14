import json

import requests

items_params = {
    "name": "",
    "key_": "",
    "type": 0,
    "value_type": 0,
    "delay": "",
    "units": "",
    "history": "{$MONIPRO_HISTORY_DAYS}",
    "trends": "{$MONIPRO_TRENDS_DAYS}",
    "hostid": "<HOST_ID>",
    "description": "",
}

trigger_params = {
    "description": "",
    "expression": "",
    "priority": 0,
    "comments": "",
}


def get_data():
    url = "http://4.233.79.31:8080/api_jsonrpc.php"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 98822a8062620e621d93240ce8ad0be8",
    }
    body = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "templateids": "10343",
            "output": "extend",
            "selectFunctions": "extend",
            "expandExpression": True,
            "templated": True,
        },
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

            cleaned_results = []
            for result in result_items:
                cleaned = {
                    key: value for key, value in result.items() if key in trigger_params
                }
                cleaned_results.append(cleaned)

            with open("cleaned_data.json", "w") as f:
                json.dump(cleaned_results, f, indent=4)
            with open("orginal_data.json", "w") as f:
                json.dump(result_items, f, indent=4)

            print("✅ Data saved to data.json")
            return data

        except json.JSONDecodeError as e:
            print(f"❌ Failed to decode JSON: {e}")
            print("Raw Response Text:", response.text[:500])
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


get_data()

# cleaned = {key: value for key, value in result.items() if value != ""}
#########################**item**##########################

# body = {
#     "jsonrpc": "2.0",
#     "method": "item.get",
#     "params": {
#         "output": "extend",
#         "templateids": "10343",
#         "templated": True,
#     },
#     "id": 1,
# }

# print("Sending request...")

# try:
#     response = requests.post(url, headers=headers, json=body)
#     response.raise_for_status()

#     try:
#         data = response.json()

#         if "error" in data:
#             print("🚨 API Error Returned:")
#             print(data["error"])
#             return None

#         result_items = data.get("result")
#         if not result_items:
#             print("⚠️ No result found in response.")
#             return None

#         cleaned_results = []
#         for result in result_items:
#             cleaned = {
#                 key: value for key, value in result.items() if key in items_params
#             }
#             cleaned["hostid"] = "10741"

#             if cleaned["history"] == "0":
#                 cleaned["history"] = "0"
#             else:
#                 cleaned["history"] = "{$MONIPRO_HISTORY_DAYS}"

#             if cleaned["trends"] == "0":
#                 cleaned["trends"] = "0"
#             else:
#                 cleaned["trends"] = "{$MONIPRO_TRENDS_DAYS}"
#             cleaned_results.append(cleaned)

#########################**trigger**##########################

# body = {
#     "jsonrpc": "2.0",
#     "method": "trigger.get",
#     "params": {
#         "templateids": "10343",
#         "output": "extend",
#         "selectFunctions": "extend",
#         "expandExpression": True,
#         "templated": True,
#     },
#     "id": 1,
# }

# print("Sending request...")

# try:
#     response = requests.post(url, headers=headers, json=body)
#     response.raise_for_status()

#     try:
#         data = response.json()

#         if "error" in data:
#             print("🚨 API Error Returned:")
#             print(data["error"])
#             return None

#         result_items = data.get("result")
#         if not result_items:
#             print("⚠️ No result found in response.")
#             return None

#         cleaned_results = []
#         for result in result_items:
#             cleaned = {
#                 key: value for key, value in result.items() if key in trigger_params
#             }
#             cleaned_results.append(cleaned)
