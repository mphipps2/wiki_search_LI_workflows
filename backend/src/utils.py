from typing import List

from src.tools import WikiSearchResult, WikiArticle

def get_context(response) -> List[str]:
    content = []  
    for source in response['sources']:
        tool_output = source.raw_output
        if isinstance(tool_output, list) and all(isinstance(item, WikiSearchResult) for item in tool_output):
            for result in tool_output:
                content.append(f"Title: {result.title}, URL: {result.url}")
        elif isinstance(tool_output, WikiArticle):
            content.append(f"Title: {tool_output.title}, Content: {tool_output.content}, URL: {tool_output.url}")
    return content
