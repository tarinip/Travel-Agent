import os
import re
from datetime import datetime
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from state import AgentState
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def clean_list(text):
    text = re.sub(r"^\d+[.]\s*", "", text)
    text = text[:1].upper() + text[1:]
    return text

def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Creates a research plan and provides filtered booking links.
    """
    query = state.get("rewritten_query", "")
    current_date = datetime.now().strftime("%A, %B %d, %Y")

    # Use the flags already extracted by rewrite_node
    is_senior = state.get("has_seniors", False)
    is_kid = state.get("has_kids", False)

    # Extract destination/dates for link construction (Assuming they exist in state)
    # If your state doesn't have these yet, we use the query as a fallback
    destination = state.get("destination", "India")

    print(f"--- 📅 PLANNER: Strategy for {query} ---")

    planner_prompt = (
        f"Today is {current_date}. You are a Travel Logistics Architect.\n"
        f"USER REQUEST: {query}\n"
        f"CONSTRAINTS: Senior Citizen: {is_senior}, Kids Friendly: {is_kid}\n\n"
        "TASK: Create a list of  search queries to find real-time prices for flights, "
        "trains , and hotels for this trip.\n\n"
        "Output ONLY the search queries, one per line."
    )

    response = llm.invoke([HumanMessage(content=planner_prompt)])
    tasks = response.content.strip().split("\n")
    tasks = [clean_list(t) for t in tasks if t != '```']

    # --- 🔗 DYNAMIC BOOKING LINKS ---
    # Constructing a basic filtered MakeMyTrip search URL (Standard format)
    # Note: Real production links usually require city codes, but we can use search terms
    mmt_hotel_link = f"https://www.makemytrip.com/hotels/hotel-listing/?city={destination}"
    mmt_flight_link = "https://www.makemytrip.com/flights/"
    irctc_link = "https://www.irctc.co.in/nget/train-search"

    booking_footer = (
        "\n\n### 🔗 Quick Booking Links:\n"
        f"* **Trains:** [Book on IRCTC Official]({irctc_link})\n"
        f"* **Hotels in {destination.title()}:** [View on MakeMyTrip]({mmt_hotel_link})\n"
        f"* **Flights:** [Check Availability on MakeMyTrip]({mmt_flight_link})"
    )

    return {
        "plan": tasks,
        "active_task_description": f"Created {len(tasks)} research tasks with accessibility filters.",
        # We store the booking info in research_data so the synthesizer can show it to the user
        "research_data": [f"BOOKING_LINKS: {booking_footer}"]
    }
