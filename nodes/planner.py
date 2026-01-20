from typing import Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from state import AgentState
from dotenv import load_dotenv
load_dotenv()
# Load environment variables

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def planner_node(state: AgentState) -> Dict[str, Any]:
    query = state.get("rewritten_query", "")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # Analyze the query for passenger types
    is_senior = any(k in query.lower() for k in ["senior", "elder", "parents"])
    is_kid = any(k in query.lower() for k in ["kid", "child", "baby", "toddler"])

    print(f"--- 📅 PLANNER: Strategy for {query} ---")

    planner_prompt = (
        f"Today is {current_date}. You are a Travel Logistics Architect.\n"
        f"USER REQUEST: {query}\n"
        f"CONSTRAINTS: Senior Citizen: {is_senior}, Kids Friendly: {is_kid}\n\n"
        "Task: Create a detailed research plan to find the following specific details:\n"
        
        "1. FLIGHTS: Direct routes, airline options, and current prices for the specified dates. "
        f"{'Focus on airlines with best wheelchair assistance/short boarding.' if is_senior else ''}\n"
        
        "2. TRAINS: Identify specific train names (e.g., Vande Bharat, Rajdhani), travel classes (1AC/2AC), "
        "and seat availability for the route.\n"
        
        "3. ROOMS: Find specific hotel names with rates. "
        f"{'Must include hotels with elevators and grab-bars.' if is_senior else ''} "
        f"{'Must include resorts with kids clubs/play areas.' if is_kid else ''}\n"
        
        "Output: Return a list of 5-7 specific search queries that will help find these EXACT prices and availability."
    )

    response = llm.invoke([HumanMessage(content=planner_prompt)])
    # We split the response into a list of tasks for the research node
    tasks = response.content.strip().split("\n")
    
    return {
        "plan": tasks,
        "current_task": "PLAN_READY"
    }