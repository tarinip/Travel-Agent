from typing import Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from utils.tools import web_search_tool, scrape_webpage
from state import AgentState
from dotenv import load_dotenv
from langgraph.config import get_stream_writer

load_dotenv()
logger = logging.getLogger(__name__)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def deep_research_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes the multi-step research plan and stores distilled findings.
    """
    plan = state.get("plan", [])
    new_findings = []
    writer = get_stream_writer()

    print(f"--- 🔍 DEEP RESEARCH: Executing {len(plan)} tasks ---")

    for i, task in enumerate(plan):
        # Update the UI status for each specific search
        status_text = f"🔍 Searching ({i+1}/{len(plan)}): {task}"
        print(status_text)
        writer({
            "node": "deep_research_node",
            "status": status_text
        })

        try:
            # 1. Fetch search results (links and snippets)
            search_results = await web_search_tool(task)

            if not search_results:
                logger.warning(f"No results found for task: {task}")
                scraped_data_combined = "No search results found."
            else:
                scraped_data_combined = ""
                # 2. Iterate through links and scrape full webpage content
                for idx, result in enumerate(search_results):
                    link = result.get("link")
                    title = result.get("title")
                    snippet = result.get("snippet")

                    status_update = f"📄 Scraping ({idx+1}/{len(search_results)}): {title[:50]}..."
                    print(status_update)
                    writer({
                        "node": "deep_research_node",
                        "status": status_update
                    })

                    if link:
                        full_content = await scrape_webpage(link)
                        scraped_data_combined += f"\n--- Source: {title} ({link}) ---\n"
                        scraped_data_combined += f"Snippet: {snippet}\n"
                        scraped_data_combined += f"Full Content: {full_content}\n\n"
                    else:
                        scraped_data_combined += f"\n--- Source: {title} ---\n"
                        scraped_data_combined += f"Snippet: {snippet}\n\n"

            # 3. Distill data into a consistent format
            # We ask the LLM to provide a "Traveler's Summary" for each search query
            distill_prompt = (
                "You are a Travel Research Specialist. Extract the most important details "
                "from the following search results and scraped webpage content for 2026 travel planning.\n\n"
                "CRITICAL DATA TO EXTRACT:\n"
                "- Exact Prices (if found)\n"
                "- Specific Hotel/Flight/Train names\n"
                "- Availability warnings\n"
                "- Direct Booking URLs\n\n"
                f"TASK: {task}\n"
                "RESEARCH DATA:\n"
                f"{scraped_data_combined[:15000]}" # Truncating to stay within context limits
            )

            # Use a simpler streaming approach to avoid redundancy
            task_summary = ""
            writer({
                "node": "deep_research_node",
                "content": f"\n\n✅ **Researching '{task}':**\n"
            })

            async for chunk in llm.astream([HumanMessage(content=distill_prompt)]):
                if chunk.content:
                    print(chunk.content)
                    task_summary += chunk.content
                    # Push the token to Chainlit immediately
                    writer({
                        "node": "deep_research_node",
                        "content": chunk.content
                    })

            new_findings.append(f"### Research Task: {task}\n{task_summary}")

        except Exception as e:
            logger.error(f"Error in deep_research_node for task '{task}': {e}")
            error_msg = f"Failed to research '{task}' due to an internal error."
            new_findings.append(f"### Research Task: {task}\n{error_msg}")
            writer({
                "node": "deep_research_node",
                "content": f"\n\n❌ **Error for '{task}':** {str(e)}"
            })

    # 3. Return updates (will be merged into state via operator.add)
    # We use active_task_description to show progress in the Chainlit sidebar
    return {
        "research_data": new_findings,
        "active_task_description": f"Successfully researched {len(plan)} items including flights and accommodation."
    }
