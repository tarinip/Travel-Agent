from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from utils.tools import web_search_tool  # Using your scraper tool
from state import AgentState
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def deep_research_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes the research plan by iterating through all search queries
    and distilling the results into the research_data state.
    """
    plan = state.get("plan", [])
    research_results = []

    print(f"--- 🔍 DEEP RESEARCH: Executing {len(plan)} tasks ---")

    for task in plan:
        print(f"Searching for: {task}...")
        
        # 1. Fetch raw data from DuckDuckGo
        raw_data = web_search_tool(task)

        # 2. Distill the data (Extract only what's useful)
        # We don't want to save the whole HTML; just the facts.
        distill_prompt = (
            "You are a Travel Data Extractor. Below is raw search data for a specific task.\n"
            "Extract only the relevant facts: names, prices, dates, links, and locations.\n"
            "If the data is irrelevant or empty, say 'No relevant data found'.\n\n"
            f"TASK: {task}\n"
            f"RAW DATA: {raw_data[:4000]}" # Truncate to save tokens
        )

        distilled_info = llm.invoke([HumanMessage(content=distill_prompt)]).content
        research_results.append(f"TASK: {task}\nRESULT: {distilled_info}")

    return {
        "research_data": research_results,
        "current_task": "RESEARCH_COMPLETED"
    }