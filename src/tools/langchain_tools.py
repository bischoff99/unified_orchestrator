"""LangChain Tools Integration - Web Search & Research"""
from crewai.tools import tool
from typing import Optional

# Lazy imports for performance
_search_tool = None
_wiki_tool = None


def _get_search_tool():
    """Lazy load DuckDuckGo search"""
    global _search_tool
    if _search_tool is None:
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            _search_tool = DuckDuckGoSearchRun()
        except ImportError:
            raise ImportError("Install: pip install langchain-community duckduckgo-search")
    return _search_tool


def _get_wiki_tool():
    """Lazy load Wikipedia"""
    global _wiki_tool
    if _wiki_tool is None:
        try:
            from langchain_community.tools import WikipediaQueryRun
            from langchain_community.utilities import WikipediaAPIWrapper
            _wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        except ImportError:
            raise ImportError("Install: pip install langchain-community wikipedia")
    return _wiki_tool


@tool("Web Search")
def web_search(query: str) -> str:
    """
    Search the web for current information using DuckDuckGo.
    
    Args:
        query: Search query string
        
    Returns:
        Search results summary
    """
    try:
        search = _get_search_tool()
        result = search.run(query)
        return f"🔍 Search results for '{query}':\n\n{result}"
    except Exception as e:
        return f"❌ Web search failed: {str(e)}"


@tool("Wikipedia Search")
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for detailed information on a topic.
    
    Args:
        query: Topic to search for
        
    Returns:
        Wikipedia article summary
    """
    try:
        wiki = _get_wiki_tool()
        result = wiki.run(query)
        return f"📚 Wikipedia on '{query}':\n\n{result}"
    except Exception as e:
        return f"❌ Wikipedia search failed: {str(e)}"


# Export tools
__all__ = ['web_search', 'wikipedia_search']

