# from typing import Dict, Any
# from langchain_core.messages import HumanMessage
# from langgraph.types import interrupt, Command
# from state import AgentState

# def human_interrupter_node(state: AgentState) -> Command:
#     # 1. Check if we have an answer already from a 'resume'
#     # LangGraph passes the resume value into the state during the resume step
#     # but the cleanest way is to handle the interrupt carefully:
    
#     if state.get("is_incomplete"):
#         reason = state.get("rewritten_query", "more details")
        
#         print("--- ⏸️ ENTERING INTERRUPT ---")
        
#         # When you resume, this 'interrupt' call returns the value from Command(resume=...)
#         # user_answer = interrupt({
#         #     "question": f"I need more info: {reason}",
#         #     "current_context": state.get("rewritten_query")
#         # })
#         user_answer = input(f"I need more info: {reason}")
        
#         # --- EVERYTHING BELOW THIS LINE ONLY RUNS AFTER RESUME ---
#         print("--- 🔄 POST-INTERRUPT EXECUTION ---")
#         print(f"Received: {user_answer}")

#         new_messages = state["messages"] + [HumanMessage(content=str(user_answer))]
#         print(f"Updated History: {new_messages}")

#         return Command(
#             update={
#                 "messages": new_messages,
#                 "is_incomplete": False,
#                 "rewritten_query": "" 
#             },
#             goto="rewrite_node"
#         )

#     # 2. Logic to proceed if NOT incomplete
#     target = "planner_node" if state.get("mode") == "planner" else "quick_lookup_node"
#     return Command(goto=target)
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