import logging
import time
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.functions.visualization_functions import (
    get_history_for_items,
    get_items_for_host,
    suggest_visualization_for_item,
)

# Set up proper logging
logger = logging.getLogger("zabbix")


class HostVisualizationsView(APIView):
    """
    API endpoint to get enriched monitoring data with visualization hints for a host.

    This endpoint provides visualization-ready data for monitoring items, including:
    - Appropriate chart type suggestions based on item characteristics
    - Historical data formatted for charting libraries
    - Metadata for proper display and interpretation

    Query Parameters:
    - time_range: Optional time range in hours (default: 24)
    - limit: Optional limit for data points per item (default: 100)
    """

    def get(self, request, host_id, format=None):
        logger.info(f"Visualization request received for host_id: {host_id}")

        try:
            # Get query parameters
            time_range = request.query_params.get("time_range", "24")
            limit = request.query_params.get("limit", "100")

            try:
                time_range = int(time_range)
                limit = int(limit)
            except ValueError:
                logger.warning(
                    f"Invalid parameters: time_range={time_range}, limit={limit}"
                )
                return Response(
                    {"error": "Invalid time_range or limit parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(
                f"Fetching data with time_range={time_range}h, limit={limit} points"
            )

            # Calculate time range for history data
            time_till = int(time.time())
            time_from = time_till - (time_range * 3600)  # Convert hours to seconds

            # 1. Get all items for the host
            logger.info(f"Fetching items for host ID {host_id}")
            items = get_items_for_host(host_id)

            if not items:
                logger.warning(f"No items found for host ID {host_id}")
                return Response(
                    {"error": f"No items found for host ID {host_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            logger.info(f"Found {len(items)} items for host ID {host_id}")

            # Group items by application/category for better organization
            item_groups = {}
            standalone_items = []

            # 2. Process each item to add visualization hint and fetch history
            for item in items:
                try:
                    item_id = item.get("itemid", "unknown")
                    item_name = item.get("name", "unknown")
                    logger.debug(f"Processing item: {item_name} (ID: {item_id})")

                    # Get visualization suggestion
                    suggestion = suggest_visualization_for_item(item)

                    # Skip items with unknown visualization type
                    if suggestion["type"] == "unknown":
                        logger.debug(
                            f"Skipping item with unknown visualization type: {item_name}"
                        )
                        continue

                    # Fetch history for this item if it's a numeric type
                    chart_data = []
                    if int(item.get("value_type", "-1")) in [
                        0,
                        3,
                    ]:  # float, numeric unsigned
                        logger.debug(f"Fetching history for item: {item_name}")
                        history = get_history_for_items(
                            item_ids=[item["itemid"]],
                            value_type=item["value_type"],
                            limit=limit,
                            time_from=time_from,
                            time_till=time_till,
                        )

                        # Format history for charting libraries
                        chart_data = []
                        for h in history:
                            try:
                                value = float(h.get("value", 0))
                                chart_data.append(
                                    {
                                        "time": int(h.get("clock", 0)),
                                        "value": value,
                                        "formatted": self._format_value(
                                            value, item.get("units", "")
                                        ),
                                    }
                                )
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Error formatting history value: {e}")

                    # Create visualization item with enhanced metadata
                    viz_item = {
                        "id": item.get("itemid", ""),
                        "name": item.get("name", ""),
                        "key": item.get("key_", ""),
                        "units": item.get("units", ""),
                        "value_type": item.get("value_type", ""),
                        "visualization": suggestion,
                        "data": chart_data,
                    }

                    # Group items by application if available
                    category = self._determine_category(item)

                    if category:
                        if category not in item_groups:
                            item_groups[category] = []
                        item_groups[category].append(viz_item)
                    else:
                        standalone_items.append(viz_item)

                except Exception as item_error:
                    logger.error(
                        f"Error processing item {item.get('name', 'unknown')}: {str(item_error)}"
                    )
                    # Continue with next item instead of failing the whole request
                    continue

            # Prepare the final response
            response_data = {
                "host_id": host_id,
                "time_range": {
                    "from": time_from,
                    "till": time_till,
                    "from_formatted": self._format_timestamp(time_from),
                    "till_formatted": self._format_timestamp(time_till),
                },
                "groups": [
                    {"name": group_name, "items": items_list}
                    for group_name, items_list in item_groups.items()
                ],
                "standalone_items": standalone_items,
            }

            logger.info(f"Successfully processed visualization data for host {host_id}")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in HostVisualizationsView: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _determine_category(self, item):
        """
        Determine the category for an item based on its key and name
        """
        try:
            key = item.get("key_", "").lower()
            name = item.get("name", "").lower()

            # Network related
            if any(x in key for x in ["net.", "icmp", "tcp", "udp", "ftp", "http"]):
                return "Network"

            # CPU related
            if "cpu" in key or "cpu" in name:
                return "CPU"

            # Memory related
            if any(x in key or x in name for x in ["mem", "memory", "swap"]):
                return "Memory"

            # Disk/Storage related
            if any(x in key for x in ["vfs", "disk", "fs.", "storage"]):
                return "Storage"

            # System related
            if "system" in key:
                return "System"

            # Process related
            if "proc" in key or "process" in name:
                return "Processes"

            # Default - no category
            return None
        except Exception as e:
            logger.warning(f"Error determining category: {e}")
            return None

    def _format_value(self, value, unit):
        """
        Format a value based on its unit for display
        """
        try:
            if unit == "%":
                return f"{value:.1f}%"
            elif unit.upper() in ["B", "KB", "MB", "GB", "TB"]:
                # Simple byte formatting
                if unit == "B" and value > 1024:
                    if value > 1024 * 1024:
                        return f"{value / (1024 * 1024):.2f} MB"
                    return f"{value / 1024:.2f} KB"
                return f"{value} {unit}"
            elif unit in ["s", "ms"]:
                if unit == "s" and value < 0.1:
                    return f"{value * 1000:.1f} ms"
                return f"{value} {unit}"
            else:
                # Default formatting
                return f"{value} {unit}" if unit else f"{value}"
        except Exception as e:
            logger.warning(f"Error formatting value {value} with unit {unit}: {e}")
            return f"{value} {unit}" if unit else f"{value}"

    def _format_timestamp(self, timestamp):
        """
        Format a Unix timestamp to a human-readable date/time
        """
        try:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"Error formatting timestamp {timestamp}: {e}")
            return str(timestamp)
