from .request import send_request


def get_history_for_items(
    item_ids, value_type, limit=100, time_from=None, time_till=None
):
    """
    Get history data for specified items

    Args:
        item_ids (list): List of item IDs
        value_type (str): Value type (0=float, 3=unsigned, etc.)
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        time_from (int, optional): Start time as Unix timestamp. Defaults to None.
        time_till (int, optional): End time as Unix timestamp. Defaults to None.

    Returns:
        list: History data sorted by time (oldest first)
    """
    params = {
        "output": "extend",
        "itemids": item_ids,
        "sortfield": "clock",
        "sortorder": "DESC",
        "limit": limit,
        "history": value_type,
    }

    # Add time range if specified
    if time_from:
        params["time_from"] = time_from
    if time_till:
        params["time_till"] = time_till

    history_data = send_request("history.get", params)

    # Return in chronological order (oldest first)
    return history_data[::-1]
