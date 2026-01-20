import requests
from typing import List, Dict, Any

# Your starting point URL
DDG_INSTANT_API = "https://api.duckduckgo.com/"

def instant_answer_tool(query: str) -> str:
    """
    Direct implementation of the DuckDuckGo Instant Answer API.
    Best for: 'What is the currency of Bali?' or 'Is visa required for Japan?'
    """
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }
    try:
        response = requests.get(DDG_INSTANT_API, params=params, timeout=10)
        data = response.json()
        
        # We try to get the 'Abstract' or the 'Answer' from DDG
        answer = data.get("AbstractText") or data.get("Answer")
        if not answer:
            return "No instant answer found. Switching to web search..."
        return answer
    except Exception as e:
        return f"Instant Answer Error: {e}"

def web_search_tool(query: str) -> str:
    """
    Scrapes the DuckDuckGo HTML page for full web results.
    Best for: 'Flight routes Mumbai to Paris' or 'Bike rentals in Goa'.
    """
    # Using the 'html' subdomain for easier scraping without JavaScript
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # For now, we return the raw text to let the LLM parse it.
        # In a real scraper, you would use BeautifulSoup here.
        return response.text[:3000] # Limiting to 3000 chars for LLM context
    except Exception as e:
        return f"Web Search Error: {e}"