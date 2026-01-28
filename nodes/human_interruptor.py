
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt
from state import AgentState

def human_interrupter_node(state: AgentState) -> Dict[str, Any]:
    """
    Pauses execution to gather missing info from the user.
    Returns state updates only. Routing is handled in main.py.
    """
    print("--- ⏸️ ENTERING INTERRUPT ---")

    # 1. Prepare the question based on why the state is incomplete
    reason = state.get("rewritten_query", "I need a few more details to proceed with your request.")
    print(reason)

    # 2. Trigger the interrupt
    # This sends the 'reason' to your app.py via astream
    user_answer = interrupt(reason)

    print("--- 🔄 POST-INTERRUPT EXECUTION ---")

    # 3. Return State Updates
    # We add the user's response to the message history and
    # reset the 'is_incomplete' flag so the Rewrite Node can re-evaluate.
    return {
        "messages": [HumanMessage(content=str(user_answer))],
        "is_incomplete": False,
        "active_task_description": "Received missing details from user."
    }