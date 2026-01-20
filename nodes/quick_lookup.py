from datetime import datetime
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.tools import instant_answer_tool
from state import AgentState
from dotenv import load_dotenv
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def quick_lookup_node(state: AgentState) -> Dict[str, Any]:
    """
    Strictly uses the DuckDuckGo Instant Answer API with 
    current date context for better reasoning.
    """
    query = state.get("rewritten_query", "")
    
    # Get current date and time for the prompt
    # Example: Friday, January 16, 2026
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    print(f"--- ⚡ INSTANT LOOKUP: {query} (Date: {current_date}) ---")

    # 1. Fetch raw data from the Instant Answer API
    api_response = instant_answer_tool(query)

    # 2. Synthesize with Date Context
    # We inject the current_date into the system prompt
    prompt = (
        f"Today's date is {current_date}. You are a travel assistant. "
        "Use the following 'Instant Answer' data to answer the user's question. "
        "If the query involves relative time (like 'tomorrow' or 'next month'), "
        "calculate the specific dates based on today's date.\n\n"
        f"API DATA: {api_response}\n\n"
        f"USER QUESTION: {query}"
    )

    # Note: We still save to research_data so the graph stays consistent.
    return {
        "research_data": [f"DATE_CONTEXT: {current_date}", f"INSTANT_FACT: {api_response}"],
        "current_task": "Providing instant response with date context"
    }