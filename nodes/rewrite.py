import os
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Import your custom state
from state import AgentState

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 1. Expanded Structured Output Schema
class RewriteNodeOutput(BaseModel):
    is_safe: bool = Field(description="False if the query is harmful or inappropriate.")
    is_incomplete: bool = Field(description="True if Destination, Dates, Budget, or No. of people are missing.")
    reason: str = Field(description="The reason if the query is unsafe or incomplete.")
    mode: str = Field(description="Either 'planner' for full trips or 'quick' for simple questions.")
    
    # New fields for passenger profile
    has_kids: bool = Field(description="True if the group includes children or infants.")
    has_seniors: bool = Field(description="True if the group includes elderly travelers.")
    
    rewritten_query: str = Field(description="A search-optimized version of the user request.")

def rewrite_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes query and extracts traveler profiles.
    Returns state updates for the next node to consume.
    """
    messages = state.get("messages", [])
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

    # 2. Invoke Structured LLM
    structured_llm = llm.with_structured_output(RewriteNodeOutput)

    messages = messages[-16:]
    last_message = messages[-1]
    if type(last_message) is HumanMessage:
        content = f"Rewrite this last message to clarify the user intent. You must go throught the entire message history to get the full context:\n{last_message.content}"
        message = HumanMessage(content=content, additional_kwargs=last_message.additional_kwargs)
        messages[-1] = message
    
    analysis = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        *messages
    ])
    output_query = analysis.rewritten_query
    if analysis.is_incomplete:
        output_query = analysis.reason
    # 3. Return State Updates
    # These values will now be available in state['has_kids'] and state['has_seniors']
    return {
        "rewritten_query": output_query,
        "is_safe": analysis.is_safe,
        "is_incomplete": analysis.is_incomplete,
        "mode": analysis.mode,
        "has_kids": analysis.has_kids,
        "has_seniors": analysis.has_seniors,
        "active_task_description": f"Extracted profile: Kids={analysis.has_kids}, Seniors={analysis.has_seniors}"
    }