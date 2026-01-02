import json
import requests

GOOGLE_API_KEY="AIzaSyA74EBDIbqnPRucQ3odRg0C8q4ePMvtUWc"
GOOGLE_CSE_ID="5210a3d6106e44b9e"

def web_search_for_rm(query: str, num_results: int = 5) -> str:
    """
    Performs a web search using Google Custom Search API.

    Returns a JSON string:
    {
      "query": "...",
      "results": [
        {"title": "...", "link": "...", "snippet": "..."},
        ...
      ]
    }
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return json.dumps(
            {
                "error": "Missing Google API configuration.",
                "hint": "Set GOOGLE_API_KEY and GOOGLE_CSE_ID constants in the script."
            },
            indent=2,
            ensure_ascii=False,
        )

    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results,
    }

    try:
        resp = requests.get(endpoint, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return json.dumps(
            {"error": "Failed to call Google Custom Search API", "details": str(e)},
            indent=2,
            ensure_ascii=False,
        )

    data = resp.json()
    items = data.get("items", [])

    results = []
    for item in items:
        results.append(
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            }
        )

    return json.dumps(
        {"query": query, "results": results},
        indent=2,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    # Mirror DS team example
    result = web_search_for_rm({{query}}, num_results=5)
    print(result)