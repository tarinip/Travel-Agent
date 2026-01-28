from datetime import datetime
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from utils.tools import instant_answer_tool
from state import AgentState
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def quick_lookup_node(state: AgentState) -> Dict[str, Any]:
    """
    Strictly uses the DuckDuckGo Instant Answer API and returns 
    state updates. Routing is handled in main.py.
    """
    query = state.get("rewritten_query", "")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    print(f"--- ⚡ INSTANT LOOKUP: {query} (Date: {current_date}) ---")

    # 1. Fetch raw data from the Instant Answer API
    api_response = instant_answer_tool(query)

    # 2. Synthesize with Date Context using the LLM
    prompt = (
        f"Today's date is {current_date}. You are a helpful travel assistant.\n\n"
        "INSTRUCTIONS:\n"
        "- Use the 'API DATA' provided below to answer the user's question.\n"
        "- If the data is insufficient, provide the best possible answer or state what is missing.\n"
        "- If the query involves relative time (e.g., 'tomorrow'), calculate specific dates based on today.\n\n"
        f"API DATA: {api_response}\n\n"
        f"USER QUESTION: {query}"
    )

    # Generate the synthesized response
    response = llm.invoke(prompt)

    # 3. Return State Updates
    # We add the result to 'messages' so the user can see it,
    # and update 'research_data' for the internal log.
    return {
        "messages": [AIMessage(content=response.content)],
        "research_data": [f"DATE_CONTEXT: {current_date}", f"INSTANT_FACT: {api_response}"],
        "active_task_description": "Completed quick lookup using search tools."
    }