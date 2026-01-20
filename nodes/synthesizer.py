from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from state import AgentState
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def synthesizer_node(state: AgentState) -> Dict[str, Any]:
    # Pulling state from previous research/lookup nodes
    research_results = state.get("research_data", [])
    query = state.get("rewritten_query", "")
    
    # 2026 Conversion Rate
    INR_RATE = 90.87

    system_message = (
        "You are a Senior Travel Concierge. Your task is to transform raw research data "
        "into a professional, highly presentable travel guide.\n\n"
        f"### CURRENCY: Always convert USD ($) to INR (₹) using the rate 1 USD = {INR_RATE}.\n\n"
        "### PRESENTATION RULES:\n"
        "1. DYNAMIC DURATION: Create a day-by-day itinerary for the EXACT number of days "
        "mentioned in the user query. Do not default to 3 days.\n"
        "2. NARRATIVE FLOW: Use headers, bold text, and bullet points to make it scannable.\n"
        "3. LOGISTICS: Clearly present the flight, train, and hotel details found in research "
        "with their booking links and converted INR prices.\n"
        "4. NO PLACEHOLDERS: If data is missing, omit that section. Do not make up facts.\n"
        "5. CLOSING: End with a single clear question asking if they want to proceed with booking."
    )

    # Join list of research strings into a single context block
    research_context = "\n".join(research_results) if isinstance(research_results, list) else research_results
    
    user_message = HumanMessage(content=(
        f"User Query: {query}\n\n"
        f"Raw Research State: {research_context}"
    ))

    response = llm.invoke([system_message, user_message])
    
    return {"messages": [response]}