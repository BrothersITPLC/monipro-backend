# agent/insight_agent.py
import os
from typing import Any, Dict, TypedDict

from dotenv import load_dotenv

load_dotenv()
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from agents.tools import format_alert_for_insight

BASE_URL = os.getenv("BASE_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# Define the expected state for LangGraph
class AgentState(TypedDict):
    alert: Dict[str, Any]
    explanation: str


# Step 1: Format the alert
def format_step(state: AgentState) -> AgentState:
    formatted = format_alert_for_insight.invoke({"alert": state["alert"]})
    return {"alert": state["alert"], "explanation": formatted}


# Step 2: Call GPT
llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_base=BASE_URL,
    openai_api_key=GITHUB_TOKEN,
    max_tokens=4096,
)


def explain_step(state: AgentState) -> AgentState:
    messages = [
        HumanMessage(
            content=f"Zabbix Alert Analysis - Use Zabbix 7.2 docs. Keep response to 3 SHORT sentences:\n"
            f"{state['explanation']}"
        )
    ]
    response = llm.invoke(messages)
    return {"alert": state["alert"], "explanation": response.content}


# Build the graph
def build_insight_agent():
    builder = StateGraph(AgentState)

    builder.add_node("FormatAlert", format_step)
    builder.add_node("ExplainAlert", explain_step)

    builder.set_entry_point("FormatAlert")
    builder.add_edge("FormatAlert", "ExplainAlert")
    builder.add_edge("ExplainAlert", END)

    return builder.compile()


# import os
# from azure.ai.inference import ChatCompletionsClient
# from azure.ai.inference.models import SystemMessage, UserMessage
# from azure.core.credentials import AzureKeyCredential

# endpoint = "https://models.github.ai/inference"
# model = "openai/gpt-4.1"
# token = os.environ["GITHUB_TOKEN"]

# client = ChatCompletionsClient(
#     endpoint=endpoint,
#     credential=AzureKeyCredential(token),
# )

# response = client.complete(
#     messages=[
#         SystemMessage("You are a helpful assistant."),
#         UserMessage("What is the capital of France?"),
#     ],
#     temperature=1.0,
#     top_p=1.0
#     model=model
# )

# print(response.choices[0].message.content)
