import re

from search.opensearch import ALIAS_NAME, opensearch
from search.parse_explain import parse_explain


class SearchRequest:
    def __init__(self, search_text: str = None, color: str = None, explain: bool = False):
        self.search_text = search_text
        self.color = color
        self.explain = explain

    def __str__(self):
        return f"'{self.search_text}' with color '{self.color}' and use explain {self.explain}"


def execute_query(search_request: SearchRequest):
    body = {
        "query": {
            "multi_match": {
                "query": search_request.search_text,
                "fields": ["name", "description"],
                "type": "cross_fields"
            }
        }
    }
    search_results = opensearch.search(index=ALIAS_NAME, body=body, explain=search_request.explain)
    hit = search_results["hits"]["hits"][0]
    explanation = hit["_explanation"]
    parse_explain(explanation)
