import wikipedia
from pydantic import BaseModel
from typing import List, Dict
from llama_index.core.tools import FunctionTool

class WikiSearchResult(BaseModel):
    title: str
    url: str

class WikiArticle(BaseModel):
    title: str
    content: str
    url: str

def wikipedia_similar_articles(query: str) -> List[Dict[str, str]]:
    """
    Search Wikipedia for articles similar to the given query and return titles and URLs.
    
    Use this tool to find the most promising articles for a user's query. 
    
    Query should be phrased as the most likely title of what the user is searching for.
    """
    search_results = wikipedia.search(query, results=15)
    result_list = []
    for result in search_results:
        try:
            page = wikipedia.page(result)
            result_list.append(WikiSearchResult(title=page.title, url=page.url))
        except wikipedia.exceptions.DisambiguationError:
            pass
        except wikipedia.exceptions.PageError:
            pass
    return result_list

def wikipedia_full_article(query: str) -> Dict[str, str]:
    """
    Retrieve the full Wikipedia article for the given query.
    
    Use this tool to research further once you have a promising article title.
    """
    try:
        page = wikipedia.page(query)
        return WikiArticle(title=page.title, content=page.content, url=page.url)
    except wikipedia.exceptions.DisambiguationError:
        pass
    except wikipedia.exceptions.PageError:
        pass
    return None

# Wrap these functions in a tool
similar_articles_tool = FunctionTool.from_defaults(fn=wikipedia_similar_articles)
full_article_tool = FunctionTool.from_defaults(fn=wikipedia_full_article)