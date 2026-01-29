import httpx
import logging
import trafilatura
import asyncio
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import unquote, urlparse, parse_qs
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Initialize LLM for factual refinement and fallbacks
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

DDG_INSTANT_API = "https://api.duckduckgo.com/"

# --- NEW: Quick Worker for Factual Lookups ---

async def instant_answer_tool(question: str) -> Dict[str, Any]:
    """
    High-speed worker for facts (Currency, Time, Basic Info).
    Uses DDG Instant API with an LLM fallback to ensure 'no results' never happens.
    """
    params = {
        "q": question,
        "format": "json",
        "no_redirect": "1",
        "no_html": "1",
        "skip_disambig": "1"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DDG_INSTANT_API, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()

        # Try to get Abstract, then Answer, then Related Topics
        content = data.get("AbstractText") or data.get("Answer")
        if not content and data.get("RelatedTopics"):
            content = "\n".join([
                t.get("Text", "") for t in data["RelatedTopics"][:3]
                if isinstance(t, dict) and "Text" in t
            ])

        # LLM Logic: If we have data, summarize it. If not, use internal knowledge.
        if content:
            prompt = f"Summarize this travel fact for '{question}' in one sentence: {content}"
            res = await llm.ainvoke([HumanMessage(content=prompt)])
            final_text = res.content
        else:
            # The 'Safety Net' - LLM answers from 2026 training if API is blank
            prompt = f"Provide a concise travel fact for 2026: {question}"
            res = await llm.ainvoke([HumanMessage(content=prompt)])
            final_text = res.content

        return {
            "query": question,
            "content": final_text,
            "source": data.get("AbstractURL") or "Internal Knowledge Base"
        }
    except Exception as e:
        logger.error(f"Quick worker error for {question}: {e}")
        return {"query": question, "content": "Information temporarily unavailable.", "error": str(e)}

async def batch_quick_lookup(tasks: List[str]) -> List[Dict[str, Any]]:
    """Runs multiple factual lookups in parallel for speed."""
    return await asyncio.gather(*[instant_answer_tool(t) for t in tasks])

# --- Refined: Existing Web Search Tool ---

async def web_search_tool(query: str, max_retries: int = 2) -> List[Dict[str, str]]:
    """Scrapes DuckDuckGo Lite for detailed search results (Flights, Hotels, Schedules)."""
    url = f"https://lite.duckduckgo.com/lite/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://duckduckgo.com/",
    }

    for attempt in range(max_retries + 1):
        try:
            # Add a small random delay to avoid bot detection
            await asyncio.sleep(random.uniform(1.0, 2.0) * (attempt + 1))

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=15)

                if response.status_code == 202:
                    logger.warning(f"DDG returned 202 (Accepted) for '{query}'. Attempt {attempt + 1}/{max_retries + 1}. Retrying...")
                    continue

                if response.status_code != 200:
                    logger.error(f"DDG Blocked: {response.status_code} for '{query}'")
                    if attempt < max_retries:
                        continue
                    return []

                soup = BeautifulSoup(response.text, "html.parser")
                results = []

                # Look for result links - DDG Lite uses 'result-link' class
                links = soup.find_all("a", class_="result-link")

                # Fallback: if 'result-link' not found, try finding all links in the results table
                if not links:
                    links = [a for a in soup.find_all("a") if "/l/?uddg=" in a.get("href", "")]

                for row in links:
                    link = row.get("href")
                    title = row.get_text(strip=True)

                    if link and "/l/?uddg=" in link:
                        parsed_url = urlparse(link)
                        query_params = parse_qs(parsed_url.query)
                        if 'uddg' in query_params:
                            link = unquote(query_params['uddg'][0])

                    snippet = ""
                    parent_table = row.find_parent("table")
                    if parent_table:
                        snippet_tag = parent_table.find("td", class_="result-snippet")
                        if snippet_tag:
                            snippet = snippet_tag.get_text(strip=True)

                    if link and title:
                        results.append({"title": title, "link": link, "snippet": snippet})

                if results:
                    return results[:5]

                logger.warning(f"No results found on DDG Lite for '{query}'. Attempt {attempt + 1}/{max_retries + 1}")
                if attempt < max_retries:
                    continue

        except Exception as e:
            logger.error(f"Web Search Error for '{query}' on attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                continue

    # Last Resort: If DuckDuckGo Lite is completely failing, use the Instant API
    try:
        logger.warning(f"All retries failed for '{query}'. Falling back to Instant Answer API.")
        fallback_data = await instant_answer_tool(query)
        if fallback_data and fallback_data.get("content"):
            return [{
                "title": f"Fact Check: {query}",
                "link": fallback_data.get("source", "https://duckduckgo.com"),
                "snippet": fallback_data.get("content")
            }]
    except Exception as e:
        logger.error(f"Fallback failed for '{query}': {e}")

    return []

# --- Existing: Scrape Webpage Tool ---

async def scrape_webpage(url: str) -> str:
    """Extracts clean text from a URL for deep analysis."""
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            content = trafilatura.extract(response.text)
            if not content:
                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                content = soup.get_text(separator=' ', strip=True)

            return content[:5000]
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""
