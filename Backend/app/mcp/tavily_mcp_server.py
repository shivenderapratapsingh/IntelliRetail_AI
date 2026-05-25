from tavily import TavilyClient

from mcp.server.fastmcp import FastMCP

from app.core.config import (
    TAVILY_API_KEY
)


#create mcp server

mcp = FastMCP(
    "Retail Market Intelligence MCP"
)




tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


#make search tool

@mcp.tool()
def market_research(query: str):

    """
    Search latest market trends, retail products,
    competitors, and business intelligence.
    """

    try:

        response = tavily_client.search(

            query=query,

            search_depth="advanced",

            max_results=5
        )

        return {
            "success": True,
            "results": response
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


#mcp server run

if __name__ == "__main__":

    mcp.run()