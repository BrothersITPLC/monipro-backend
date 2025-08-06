from .request import send_request


def get_items_for_host(host_id):
    params = {
        "output": ["itemid", "name", "key_", "value_type", "units"],
        "hostids": host_id,
        "sortfield": "name",
        "filter": {"status": "0"},
    }
    return send_request("item.get", params)
