import datetime
from typing import Any, Dict

from langchain_core.tools import tool


@tool
def format_alert_for_insight(alert: Dict[str, Any]) -> str:
    """
    Takes a Zabbix alert object and returns a formatted string with context,
    suitable to pass to an LLM for explanation.
    """
    trigger = alert.get("trigger", {})
    host = alert.get("host", {})
    tags = alert.get("tags", [])

    time = datetime.datetime.fromtimestamp(int(trigger.get("lastchange", 0))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    explanation_prompt = f"""Using Zabbix 7.2 documentation for your analysis (but don't mention Zabbix in your response), analyze this alert:
    
**Trigger:** {trigger.get("description")}
**Host:** {host.get("host")}
**Event Time:** {time}
**Priority:** {trigger.get("priority")}
**Status:** {"ACTIVE" if trigger.get("value") == "1" else "RESOLVED"}
**Tags:** {', '.join([f"{t['tag']}:{t['value']}" for t in tags])}

Explain in 3 sentences max without mentioning Zabbix:
1. Current system state
2. Likely cause
3. Recommended action"""

    return explanation_prompt
