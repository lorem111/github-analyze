#!/usr/bin/env python3
"""
GitHub Repository Analyzer

A simple script to analyze GitHub repositories using the GitHub API.
Takes a GitHub repository URL as input and outputs general repository information.
"""

import argparse
import re
import sys
import requests
import base64
from urllib.parse import urlparse


class GitHubAnalyzer:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})

    def parse_github_url(self, url):
        """Parse GitHub URL to extract owner and repository name."""
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, url)

        if not match:
            raise ValueError("Invalid GitHub URL format")

        owner = match.group(1)
        repo = match.group(2)

        # Remove .git suffix if present
        if repo.endswith('.git'):
            repo = repo[:-4]

        return owner, repo

    def get_readme_content(self, owner, repo):
        """Fetch README content from GitHub API."""
        readme_url = f"{self.base_url}/repos/{owner}/{repo}/readme"

        try:
            response = self.session.get(readme_url)
            response.raise_for_status()
            readme_data = response.json()

            # Decode base64 content
            content = base64.b64decode(readme_data['content']).decode('utf-8')
            return content[:100]  # Return first 100 characters
        except requests.exceptions.RequestException:
            return "README not available"
        except Exception:
            return "README content could not be decoded"

    def get_repository_info(self, url):
        """Fetch repository information from GitHub API."""
        try:
            owner, repo = self.parse_github_url(url)
        except ValueError as e:
            return {"error": str(e)}

        api_url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            response = self.session.get(api_url)
            response.raise_for_status()
            repo_data = response.json()

            # Add README content to repo data
            repo_data['readme_preview'] = self.get_readme_content(owner, repo)

            return repo_data
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}

    def format_repo_info(self, repo_data):
        """Format repository information for display."""
        if "error" in repo_data:
            return f"Error: {repo_data['error']}"

        info = []
        info.append(f"Repository: {repo_data.get('full_name', 'N/A')}")
        info.append(f"Description: {repo_data.get('description', 'No description')}")
        info.append(f"Language: {repo_data.get('language', 'N/A')}")
        info.append(f"Stars: {repo_data.get('stargazers_count', 0)}")
        info.append(f"Forks: {repo_data.get('forks_count', 0)}")
        info.append(f"Open Issues: {repo_data.get('open_issues_count', 0)}")
        info.append(f"Size: {repo_data.get('size', 0)} KB")
        info.append(f"Created: {repo_data.get('created_at', 'N/A')}")
        info.append(f"Updated: {repo_data.get('updated_at', 'N/A')}")
        info.append(f"Default Branch: {repo_data.get('default_branch', 'N/A')}")
        info.append(f"Clone URL: {repo_data.get('clone_url', 'N/A')}")
        info.append(f"Private: {repo_data.get('private', False)}")

        if repo_data.get('license'):
            info.append(f"License: {repo_data['license'].get('name', 'N/A')}")
        else:
            info.append("License: None")

        # Add README preview
        readme_preview = repo_data.get('readme_preview', 'README not available')
        info.append(f"README Preview: {readme_preview}")

        return "\n".join(info)


def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub repositories")
    parser.add_argument("url", help="GitHub repository URL")
    parser.add_argument("--token", help="GitHub API token for authenticated requests")

    args = parser.parse_args()

    analyzer = GitHubAnalyzer(token=args.token)
    repo_info = analyzer.get_repository_info(args.url)
    formatted_info = analyzer.format_repo_info(repo_info)

    print(formatted_info)


if __name__ == "__main__":
    main()