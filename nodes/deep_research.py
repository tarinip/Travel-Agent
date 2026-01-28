from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from utils.tools import web_search_tool  # Your web scraper/search tool
from state import AgentState
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def deep_research_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes the multi-step research plan and stores distilled findings.
    """
    plan = state.get("plan", [])
    # We maintain existing research_data (like booking links from Planner)
    existing_research = state.get("research_data", [])
    new_findings = []

    print(f"--- 🔍 DEEP RESEARCH: Executing {len(plan)} tasks ---")

    for i, task in enumerate(plan):
        # Update the UI status for each specific search
        print(f"Searching for ({i+1}/{len(plan)}): {task}...")
        
        # 1. Fetch raw web data
        raw_results = web_search_tool(task)

        # 2. Distill data into a consistent format
        # We ask the LLM to provide a "Traveler's Summary" for each search query
        distill_prompt = (
            "You are a Travel Research Specialist. Extract the most important details "
            "from the following search results for 2026 travel planning.\n\n"
            "CRITICAL DATA TO EXTRACT:\n"
            "- Exact Prices (if found)\n"
            "- Specific Hotel/Flight/Train names\n"
            "- Availability warnings\n"
            "- Direct Booking URLs\n\n"
            f"TASK: {task}\n"
            f"SEARCH RESULTS: {raw_results[:5000]}" # Truncating to stay within context limits
        )

        distilled_info = llm.invoke([HumanMessage(content=distill_prompt)]).content
        new_findings.append(f"### Research Task: {task}\n{distilled_info}")

    # 3. Combine with previous state and return
    # We use active_task_description to show progress in the Chainlit sidebar
    return {
        "research_data": existing_research + new_findings,
        "active_task_description": f"Successfully researched {len(plan)} items including flights and accommodation."
    }