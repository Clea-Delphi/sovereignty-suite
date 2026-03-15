#!/usr/bin/env python3
import os, requests, json, sys
from urllib.parse import quote_plus

API_KEY = os.getenv('BRAVE_API_KEY')
if not API_KEY:
    print("Error: BRAVE_API_KEY not set", file=sys.stderr)
    sys.exit(1)

def brave_search(query, count=10):
    url = "https://api.search.brave.com/results/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": API_KEY
    }
    params = {
        "q": query,
        "count": count,
        "freshness": "month"  # recent
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    if resp.status_code != 200:
        print(f"Brave API error {resp.status_code}: {resp.text}", file=sys.stderr)
        return []
    data = resp.json()
    # Extract web results
    results = []
    for item in data.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("snippet")
        })
    return results

if __name__ == "__main__":
    queries = [
        "AI agent memory architecture 2025",
        "self-verification autonomous agents",
        "agent authentication protocols",
        "episodic semantic procedural memory agents"
    ]
    all_results = {}
    for q in queries:
        print(f"Searching: {q}")
        res = brave_search(q, count=5)
        all_results[q] = res
    print(json.dumps(all_results, indent=2))
