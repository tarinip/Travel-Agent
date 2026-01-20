# import os
# from typing import Dict, Any
# from datetime import datetime
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage

# # Import your custom state
# from state import AgentState

# # Load environment variables
# load_dotenv()

# # Initialize LLM
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# def rewrite_node(state: AgentState) -> Dict[str, Any]:
#     """
#     1. Manages rolling window.
#     2. Checks safety and completeness.
#     3. Decides execution path: 'quick' vs 'planner'.
#     """
    
#     # 1. Rolling Window Logic
#     messages = state.get("messages", [])
#     trimmed_messages = messages[-10:]
    
#     # FIXED: Using the variable 'trimmed_messages' instead of the function 'trim_messages'
#     last_user_query = trimmed_messages[-1].content if trimmed_messages else ""

#     # 2. Get Current Date for Context
#     current_date = datetime.now().strftime("%A, %B %d, %Y")

#     # 3. Enhanced System Prompt with Date Context
#     system_prompt = (
#         f"Today's date is {current_date}. "
#         "You are a Travel Architect Orchestrator. Analyze the query and provide a status-prefixed response.\n\n"
#         "TASKS:\n"
#         "1. SAFETY: If harmful, return 'UNSAFE: <reason>'.\n"
#         "2. COMPLETENESS: If the user wants a full plan but lacks Destination, Dates, or Budget, "
#         "return 'INCOMPLETE: <missing info>'.\n"
#         "3. MODE SELECTION:\n"
#         "   - If it is a simple question or single recommendation (e.g., 'Cafe in Mumbai'), set MODE: QUICK.\n"
#         "   - If it is a request for a trip, itinerary, or involves logistics (flights/hotels/cabs), set MODE: PLANNER.\n"
#         "4. REWRITE: Provide a search-optimized version of the query. If the user uses relative dates (e.g., 'next Monday'), "
#         "convert them to absolute dates based on today's date."
#     )

#     # 4. LLM Execution
#     prompt_content = f"{system_prompt}\n\nUser Query: {last_user_query}"
#     response = llm.invoke([HumanMessage(content=prompt_content)]).content

#     # 5. Parsing the Decision
#     mode = "quick" # Default
#     if "MODE: PLANNER" in response:
#         mode = "planner"
#     elif "MODE: QUICK" in response:
#         mode = "quick"

#     return {
#         "rewritten_query": response,
#         "messages": trimmed_messages,
#         "is_safe": not response.startswith("UNSAFE"),
#         "is_incomplete": response.startswith("INCOMPLETE"),
#         "mode": mode 
#     }
import os
from typing import Dict, Any, Union
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.types import Command

# Import your custom state
from state import AgentState

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def rewrite_node(state: AgentState) -> Union[Dict[str, Any], Command]:
    """
    Analyzes query, extracts metadata, and routes to the next node.
    """
    messages = state.get("messages", [])
    print(messages)
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    system_prompt = (
        f"Today's date is {current_date}. "
        "You are a Travel Architect Orchestrator. Analyze the query and provide a status-prefixed response.\n\n"
        "TASKS:\n"
        "1. SAFETY: If harmful, return 'UNSAFE: <reason>'.\n"
        "2. COMPLETENESS: Only return 'INCOMPLETE' if the any of the following are missing:\n"
        "   - Destination\n"
        "   - Dates\n"
        "   - Budget\n"
        "   - No of people\n"
        "   Make sure to include a reason for INCOMPLETE.\n"
        "   If preferences in vacation type or preferred activities are OPTIONAL. Even if they are missing, DO NOT mark as INCOMPLETE; instead, proceed with MODE: PLANNER and use reasonable defaults (e.g., 3 days, mid-range budget).\n"
        "3. CONTEXT: If a detail was mentioned earlier in the HISTORY, it is still valid.\n"
        "4. MODE SELECTION:\n"
        "   - MODE: QUICK (Simple questions, single tips).\n"
        "   - MODE: PLANNER (Full trips, itineraries, logistics).\n"
        "5. REWRITE: Provide a search-optimized version of the query." 
     )

    response = llm.invoke([SystemMessage(content=system_prompt), *messages])
    messages.append(response)
    response = response.content
    print(response)

    # 2. Extract state variables from LLM response
    is_safe = "UNSAFE" in response
    is_incomplete = "INCOMPLETE" in response

    print(is_incomplete)
    
    mode = "quick"
    if "MODE: PLANNER" in response:
        mode = "planner"

    # 3. Build Update Dictionary
    update_data = {
        "rewritten_query": response,
        "is_safe": is_safe,
        "is_incomplete": is_incomplete,
        "mode": mode 
    }

    # 4. NODE-BASED ROUTING (Replaces master_router)
    if not is_safe or is_incomplete:
        # Route to Human Interrupter to fix the query
        return Command(update=update_data, goto="human_interrupter_node")
    
    if mode == "planner":
        return Command(update=update_data, goto="planner_node")
    
    # Default to Quick Lookup
    return Command(update=update_data, goto="quick_lookup_node")