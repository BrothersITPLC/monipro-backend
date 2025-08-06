import re


def suggest_visualization_for_item(item):
    """
    Analyzes a single Zabbix item and suggests a visualization type and options.

    This function uses a decision tree approach to determine the most appropriate
    visualization type based on the item's characteristics.

    Args:
        item (dict): Zabbix item data containing keys like value_type, units, key_, name, etc.

    Returns:
        dict: Visualization suggestion with type and options
    """
    value_type = int(item.get("value_type", -1))
    units = item.get("units", "")
    key = item.get("key_", "")
    name = item.get("name", "")
    description = item.get("description", "")

    # Extract additional context from name and description
    name_lower = name.lower()
    desc_lower = description.lower()

    # Rule 1: Non-graphable data (text, log)
    if value_type in [1, 2, 4]:  # char, log, text
        return {
            "type": "text-display",
            "options": {"title": name, "description": description},
        }

    # Rule 2: Uptime/Time-based data
    if (
        "uptime" in key
        or "uptime" in name_lower
        or "boot time" in name_lower
        or "unixtime" in units
    ):
        return {
            "type": "single-stat",
            "options": {
                "title": name,
                "format": "duration",
                "description": description,
            },
        }

    # Rule 3: Boolean/Status data (up/down, on/off)
    if value_type == 3 and any(
        x in key for x in ["status", "state", "available", "ping"]
    ):
        if "icmpping" in key and not "loss" in key and not "sec" in key:
            return {
                "type": "status-indicator",
                "options": {
                    "title": name,
                    "description": description,
                },
            }

    # Rule 4: Percentage-based data
    if units == "%":
        # CPU, Memory, Disk usage percentages - good for gauges
        if any(
            x in name_lower or x in key
            for x in ["cpu", "memory", "disk", "space", "usage", "util"]
        ):
            return {
                "type": "gauge",
                "options": {
                    "title": name,
                    "min": 0,
                    "max": 100,
                    "unit": "%",
                    "description": description,
                },
            }

        # ICMP packet loss - good for line chart with thresholds
        if "loss" in key or "loss" in name_lower:
            return {
                "type": "line",
                "options": {
                    "title": name,
                    "unit": "%",
                    "description": description,
                    "yaxis": {"min": 0, "max": 100},
                },
            }

        # Default for other percentages
        return {
            "type": "line",
            "options": {
                "title": name,
                "unit": "%",
                "description": description,
                "yaxis": {"min": 0, "max": 100},
            },
        }

    # Rule 5: Network Traffic (bits or bytes per second)
    if any(x in units.lower() for x in ["bps", "b/s", "bytes/s", "bits/s"]):
        return {
            "type": "area-chart",
            "options": {
                "title": name,
                "unit": units,
                "description": description,
                "stacked": False,
                "gradient": True,
            },
        }

    # Rule 6: Data sizes (memory, disk space)
    if units.upper() in ["B", "KB", "MB", "GB", "TB"]:
        # Free vs Total space - good for pie charts
        if (
            "free" in key
            or "total" in key
            or "available" in name_lower
            or "used" in name_lower
        ):
            return {
                "type": "pie-chart",
                "options": {
                    "title": name,
                    "unit": units,
                    "description": description,
                    "format": "bytes",
                    "needsComplementaryData": True,  # Frontend should look for related free/total items
                },
            }

        # Time series of memory/disk usage
        return {
            "type": "line",
            "options": {
                "title": name,
                "unit": units,
                "description": description,
                "format": "bytes",
            },
        }

    # Rule 7: Ping/Response time
    if "ping" in key or "response" in name_lower or units in ["s", "ms"]:
        # ICMP response time
        if "icmppingsec" in key:
            return {
                "type": "line",
                "options": {
                    "title": name,
                    "unit": units,
                    "description": description,
                },
            }

        # Web response time
        if "web" in key:
            return {
                "type": "line",
                "options": {
                    "title": name,
                    "unit": units,
                    "description": description,
                },
            }

        # Default response time
        return {
            "type": "line",
            "options": {"title": name, "unit": units, "description": description},
        }

    # Rule 8: Temperature data
    if units == "C" or units == "F" or "temp" in name_lower:
        return {
            "type": "line",
            "options": {
                "title": name,
                "unit": units,
                "description": description,
            },
        }

    # Rule 9: Process count or number of items
    if "processes" in name_lower or "count" in name_lower or "num" in key:
        return {
            "type": "bar-chart",
            "options": {"title": name, "description": description},
        }

    # Rule 10: Time-series data that doesn't fit other categories
    if value_type in [0, 3]:  # float, numeric unsigned
        return {
            "type": "line",
            "options": {"title": name, "unit": units, "description": description},
        }

    # Fallback for unknown types
    return {"type": "unknown", "options": {"title": name, "description": description}}
