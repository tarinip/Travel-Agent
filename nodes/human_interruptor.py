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
from langgraph.types import interrupt, Command
from state import AgentState

def human_interrupter_node(state: AgentState) -> Command:
    print(state)
    if state.get("is_incomplete"):
        reason = state.get("rewritten_query", "more details")
        
        # ❌ REMOVE: user_answer = input(...) 
        # ✅ USE: interrupt() - This sends the data to your app.py stream
        print("--- ⏸️ ENTERING INTERRUPT ---")
        user_answer = interrupt(f"STATUS: INCOMPLETE. Reason: {reason}")
        
        # This code ONLY runs AFTER the user replies and the graph resumes
        print("--- 🔄 POST-INTERRUPT EXECUTION ---")
        
        return Command(
            update={
                "messages": [HumanMessage(content=str(user_answer))],
                "is_incomplete": False,
                "rewritten_query": "" 
            },
            goto="rewrite_node"
        )

    target = "planner_node" if state.get("mode") == "planner" else "quick_lookup_node"
    return Command(goto=target)