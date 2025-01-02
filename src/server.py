from fastmcp import FastMCP
import httpx
from urllib.parse import urlparse
import os

mcp = FastMCP("search", dependencies=["uvicorn"])

JINAAI_SEARCH_URL = "https://s.jina.ai/"
JINAAI_READER_URL = "https://r.jina.ai/"
JINAAI_GROUNDING_URL = "https://g.jina.ai/"
JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")


def is_valid_url(url: str) -> bool:
    """
    Validate if the given string is a proper URL.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


@mcp.tool()
async def read(query_or_url: str) -> str:
    """
    Read content from a URL or perform a search query.
    """
    try:
        if not JINAAI_API_KEY:
            return "JINAAI_API_KEY environment variable is not set"

        headers = {
            "Authorization": f"Bearer {JINAAI_API_KEY}",
            "X-Retain-Images": "none",
            "X-Timeout": "20",
            "X-Locale": "en-US",
        }

        async with httpx.AsyncClient() as client:
            if is_valid_url(query_or_url):
                headers["X-With-Links-Summary"] = "true"
                url = f"{JINAAI_READER_URL}{query_or_url}"
            else:
                url = f"{JINAAI_SEARCH_URL}{query_or_url}"
            response = await client.get(url, headers=headers)
            return response.text
    except Exception as e:
        return str(e)


@mcp.tool()
async def fact_check(query: str) -> str:
    """
    Perform a fact-checking query.
    """
    try:
        if not JINAAI_API_KEY:
            return "JINAAI_API_KEY environment variable is not set"

        headers = {
            "Authorization": f"Bearer {JINAAI_API_KEY}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            url = f"{JINAAI_GROUNDING_URL}{query}"
            response = await client.get(url, headers=headers)
            res = response.json()
            if res["code"] != 200:
                return "Failed to fetch fact-check result"
            return res["data"]["reason"]
    except Exception as e:
        return str(e)
