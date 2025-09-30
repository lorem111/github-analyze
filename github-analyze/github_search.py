#!/usr/bin/env python3
"""
GitHub Repository Search

A script to search for GitHub repositories using keywords.
Uses the GitHub Search API to find repositories matching the search query.
"""

import argparse
import requests
import sys
from urllib.parse import quote


class GitHubSearcher:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})

    def search_repositories(self, query, limit=10, sort="stars", order="desc"):
        """Search for repositories using GitHub Search API."""
        # Encode the search query
        encoded_query = quote(query)
        search_url = f"{self.base_url}/search/repositories"

        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(limit, 100)  # GitHub API max is 100 per page
        }

        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Search request failed: {str(e)}"}

    def format_search_results(self, search_data):
        """Format search results for display."""
        if "error" in search_data:
            return f"Error: {search_data['error']}"

        if search_data.get('total_count', 0) == 0:
            return "No repositories found matching your search query."

        results = []
        results.append(f"Found {search_data.get('total_count', 0)} repositories")
        results.append("=" * 50)

        for i, repo in enumerate(search_data.get('items', []), 1):
            results.append(f"\n{i}. {repo.get('full_name', 'N/A')}")
            results.append(f"   Description: {repo.get('description', 'No description')}")
            results.append(f"   Language: {repo.get('language', 'N/A')}")
            results.append(f"   Stars: {repo.get('stargazers_count', 0)}")
            results.append(f"   Forks: {repo.get('forks_count', 0)}")
            results.append(f"   Updated: {repo.get('updated_at', 'N/A')}")
            results.append(f"   URL: {repo.get('html_url', 'N/A')}")

        return "\n".join(results)


def main():
    parser = argparse.ArgumentParser(description="Search GitHub repositories")
    parser.add_argument("--search", required=True, help="Search query for repositories")
    parser.add_argument("--token", help="GitHub API token for authenticated requests")
    parser.add_argument("--limit", type=int, default=10, help="Number of results to display (default: 10, max: 100)")
    parser.add_argument("--sort", choices=["stars", "forks", "help-wanted-issues", "updated"],
                       default="stars", help="Sort results by (default: stars)")
    parser.add_argument("--order", choices=["asc", "desc"], default="desc",
                       help="Sort order (default: desc)")

    args = parser.parse_args()

    if args.limit > 100:
        print("Warning: GitHub API limits results to 100 per page. Setting limit to 100.")
        args.limit = 100

    searcher = GitHubSearcher(token=args.token)
    search_results = searcher.search_repositories(
        query=args.search,
        limit=args.limit,
        sort=args.sort,
        order=args.order
    )
    formatted_results = searcher.format_search_results(search_results)

    print(formatted_results)


if __name__ == "__main__":
    main()