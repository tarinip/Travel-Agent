from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# Using gpt-4o for the final synthesis to ensure high-quality formatting
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

def synthesizer_node(state: AgentState) -> Dict[str, Any]:
    """
    Final node that formats all research data into a polished travel itinerary.
    """
    # 1. Pull necessary data from state
    research_results = state.get("research_data", [])
    query = state.get("rewritten_query", "")
    mode = state.get("mode", "quick") # <--- FIX: Added this line
    
    # Use the 2026 rate
    INR_RATE = 90.87

    # 2. Dynamic System Prompt based on Mode
    if mode == "quick":
        system_prompt = (
            "You are a concise travel expert. Your goal is to provide a direct answer "
            "to the user's question based ONLY on the provided research.\n\n"
            "STRICT RULES:\n"
            "1. Answer the question directly and stop.\n"
            "2. Do NOT generate a multi-day itinerary or suggestions unless the user explicitly asked for one.\n"
            "3. If pricing is involved, use the conversion 1 USD = 90.87 INR."
        )
    else:
        system_prompt = (
            "You are a Senior Travel Concierge. Your task is to transform raw research data "
            "into a professional, highly presentable travel guide for 2026.\n\n"
            f"### CURRENCY CONVERSION: Use the rate 1 USD = {INR_RATE} INR. "
            "Always show prices in ₹ (INR) first, followed by ($) in parentheses.\n\n"
            "### PRESENTATION RULES:\n"
            "1. DURATION: Create a day-by-day itinerary based on the user's requested timeframe.\n"
            "2. SCANNABILITY: Use Markdown (##, ###, **bold**) and tables where appropriate.\n"
            "3. ACCESSIBILITY: If 'has_kids' or 'has_seniors' flags are set, highlight specific amenities "
            "(e.g., 'Stroller friendly', 'Elevator access').\n"
            "4. LINKS: Ensure relevant booking links (MakeMyTrip/IRCTC) are clearly displayed.\n"
            "5. NO HALLUCINATIONS: Do not invent specific hotel prices if research data is missing."
        )

    # 3. Format Context
    research_context = "\n---\n".join(research_results) if isinstance(research_results, list) else str(research_results)
    profile_context = f"Group Profile: Kids={state.get('has_kids')}, Seniors={state.get('has_seniors')}"

    # 4. Prepare Message for LLM
    full_prompt = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=(
            f"ORIGINAL QUERY: {query}\n"
            f"TRAVELER PROFILE: {profile_context}\n\n"
            f"RAW RESEARCH FINDINGS:\n{research_context}"
        ))
    ]

    # 5. Invoke and Return
    response = llm.invoke(full_prompt)
    
    return {
        "messages": [AIMessage(content=response.content)],
        "active_task_description": "Final response generated."
    }