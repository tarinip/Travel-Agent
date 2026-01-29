
import asyncio
from utils.tools import web_search_tool

async def test():
    results = await web_search_tool("Paris hotels")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(test())
