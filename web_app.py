#!/usr/bin/env python3
"""
GitHub Search Web Interface

A Flask web application for searching GitHub repositories with README previews.
"""

from flask import Flask, render_template, request, jsonify
import requests
import base64
import os
import time
from urllib.parse import quote
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)


class MermaidDiagramGenerator:
    def __init__(self, openrouter_api_key=None):
        self.openrouter_api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        if self.openrouter_api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
            )
        else:
            self.client = None

    def generate_mermaid_diagram(self, repository_name, files):
        """Generate a Mermaid diagram based on repository file structure."""
        if not self.client:
            return "graph TD\n    A[Repository] --> B[No API key configured]"

        # Organize files by directories for better structure understanding
        file_structure = {}
        for file in files[:50]:  # Limit to 50 files to avoid token limits
            path_parts = file['path'].split('/')
            current = file_structure

            for part in path_parts[:-1]:  # All but the last part (filename)
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add the filename
            filename = path_parts[-1]
            current[filename] = file.get('size', 0)

        # Create a structured representation
        structure_text = self._dict_to_text(file_structure, 0)

        system_prompt = """
You are a Mermaid diagram generator. Create a flowchart diagram that represents the architecture and file structure of a software project.

Rules:
1. Generate a Mermaid flowchart (graph TD format)
2. Show main directories as nodes
3. Group related files under their directories
4. Use meaningful node IDs (A, B, C, etc.)
5. Show relationships between components
6. Keep it simple and readable (max 15-20 nodes)
7. Focus on important files like configs, main source files, tests, docs
8. Use descriptive labels in square brackets
9. IMPORTANT: Use individual connections only (A --> B), never use & operator
10. Each connection must be on its own line

Example format:
graph TD
    A[Project Root] --> B[src/]
    A --> C[tests/]
    B --> D[main.py]
    B --> E[utils.py]
    C --> F[test_main.py]
    D --> E

Return only the Mermaid diagram code, nothing else. Do not use markdown code blocks.
"""

        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github-analyze.local",
                    "X-Title": "GitHub Analyzer",
                },
                model="google/gemini-2.5-flash-preview-09-2025",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Repository: {repository_name}\n\nFile structure:\n{structure_text}"}
                ],
                max_tokens=400,
                temperature=0.3
            )

            response_text = completion.choices[0].message.content.strip()

            # Clean up the response to ensure it's valid Mermaid
            # Remove markdown code block markers if present
            if response_text.startswith('```mermaid'):
                response_text = response_text.replace('```mermaid', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()

            # Fix invalid & operator syntax
            lines = response_text.split('\n')
            fixed_lines = []
            for line in lines:
                if '&' in line and '-->' in line:
                    # Split lines with & into multiple individual connections
                    parts = line.split('-->')
                    if len(parts) == 2:
                        left_side = parts[0].strip()
                        right_side = parts[1].strip()

                        if '&' in left_side:
                            # Split multiple sources
                            sources = [s.strip() for s in left_side.split('&')]
                            for source in sources:
                                fixed_lines.append(f"    {source} --> {right_side}")
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            response_text = '\n'.join(fixed_lines)

            # Ensure it starts with graph directive
            if not response_text.startswith('graph'):
                response_text = "graph TD\n" + response_text

            return response_text

        except Exception as e:
            print(f"Error generating Mermaid diagram: {e}")
            return f"graph TD\n    A[{repository_name}] --> B[Error generating diagram]\n    B --> C[{str(e)[:50]}...]"

    def _dict_to_text(self, d, level=0):
        """Convert nested dictionary to readable text structure."""
        result = []
        indent = "  " * level

        for key, value in d.items():
            if isinstance(value, dict):
                result.append(f"{indent}{key}/")
                result.append(self._dict_to_text(value, level + 1))
            else:
                size_info = f" ({value} bytes)" if isinstance(value, int) and value > 0 else ""
                result.append(f"{indent}{key}{size_info}")

        return "\n".join(result)


class NaturalLanguageQueryParser:
    def __init__(self, openrouter_api_key=None):
        self.openrouter_api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        if self.openrouter_api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
            )
        else:
            self.client = None

    def parse_natural_language_query(self, user_query):
        """Convert natural language query to GitHub search terms using Gemini 2.5 Flash."""
        if not self.client:
            # Fallback: return original query if no API key
            return user_query

        system_prompt = """
You are a GitHub search query optimizer. Generate 3 different search variations for the same natural language request to maximize repository discovery.

Rules:
1. Generate exactly 3 variations, each 2-3 words
2. Each variation should approach the same concept from different angles
3. Use different technical terminology and synonyms
4. Remove unnecessary words like "I want", "find", "solution", "help me"
5. Focus on core functionality, implementation, and related concepts

Format: Return the 3 variations separated by newlines, nothing else.

Examples:
- "I want to find a solution to detect bird sound" →
bird detection
audio classification
sound recognition

- "help me build a web scraper" →
web scraper
html parser
data extraction

- "looking for machine learning models for text" →
machine learning
text classification
natural language

Generate 3 search variations, one per line:
"""

        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github-analyze.local",
                    "X-Title": "GitHub Analyzer",
                },
                model="google/gemini-2.5-flash-preview-09-2025",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=50,
                temperature=0.3
            )

            response_text = completion.choices[0].message.content.strip()
            # Split into 3 variations
            variations = [line.strip() for line in response_text.split('\n') if line.strip()]
            # Ensure we have at least one variation
            if not variations:
                return [user_query]
            # Limit to 3 variations
            return variations[:3]

        except Exception as e:
            print(f"Error parsing natural language query: {e}")
            return [user_query]


class GitHubWebSearcher:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()

        # Use provided token or check environment variables
        github_token = token or os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        if github_token:
            self.session.headers.update({"Authorization": f"token {github_token}"})
            print(f"🔑 Using GitHub token for enhanced API access")

    def get_repository_tree(self, owner, repo):
        """Fetch repository file structure from GitHub API."""
        tree_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"

        try:
            response = self.session.get(tree_url)
            print(f"🌳 File tree fetch for {owner}/{repo}: {response.status_code}")

            if response.status_code == 404:
                return {"error": "Repository not found"}
            elif response.status_code == 403:
                return {"error": "Repository access denied (add GitHub token)"}

            response.raise_for_status()
            tree_data = response.json()

            # Filter and organize files
            files = []
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':  # Only files, not directories
                    files.append({
                        'path': item['path'],
                        'size': item.get('size', 0)
                    })

            print(f"✅ Found {len(files)} files in repository")
            return {"files": files}

        except requests.exceptions.RequestException as e:
            print(f"❌ File tree fetch failed for {owner}/{repo}: {e}")
            return {"error": f"File tree fetch failed: {str(e)}"}
        except Exception as e:
            print(f"❌ File tree decode failed for {owner}/{repo}: {e}")
            return {"error": f"File tree decode failed: {str(e)}"}

    def get_readme_content(self, owner, repo):
        """Fetch README content from GitHub API."""
        readme_url = f"{self.base_url}/repos/{owner}/{repo}/readme"

        try:
            response = self.session.get(readme_url)
            print(f"📖 README fetch for {owner}/{repo}: {response.status_code}")

            if response.status_code == 404:
                return "No README found"
            elif response.status_code == 403:
                return "README available (add GitHub token for preview)"

            response.raise_for_status()
            readme_data = response.json()

            # Decode base64 content
            content = base64.b64decode(readme_data['content']).decode('utf-8')
            preview = content[:100].replace('\n', ' ').strip()
            print(f"✅ README preview: {preview[:50]}...")
            return preview

        except requests.exceptions.RequestException as e:
            print(f"❌ README fetch failed for {owner}/{repo}: {e}")
            return "README fetch failed"
        except Exception as e:
            print(f"❌ README decode failed for {owner}/{repo}: {e}")
            return "README decode failed"

    def calculate_semantic_relevance(self, original_query, repo, preferred_language=None):
        """Calculate semantic relevance score between original query and repository."""
        query_lower = original_query.lower()
        query_words = set(query_lower.split())

        # Get repository text for comparison (include README content)
        repo_name = (repo.get('name') or '').lower()
        repo_desc = (repo.get('description') or '').lower()
        repo_topics = ' '.join(repo.get('topics', [])).lower()
        readme_content = (repo.get('readme_preview') or '').lower()

        # Combine all text sources
        all_repo_text = f"{repo_name} {repo_desc} {repo_topics} {readme_content}"
        repo_words = set(all_repo_text.split())

        # Calculate base overlap
        overlap = len(query_words.intersection(repo_words))

        # Enhanced scoring with weights
        score = 0

        # Repository name matches (highest weight)
        name_matches = sum(3 for word in query_words if word in repo_name)

        # Description matches (high weight)
        desc_matches = sum(2 for word in query_words if word in repo_desc)

        # Topic matches (medium weight)
        topic_matches = sum(2 for word in query_words if word in repo_topics)

        # README content matches (medium weight)
        readme_matches = sum(1 for word in query_words if word in readme_content)

        # Exact phrase matches in any field (bonus)
        phrase_bonus = 0
        if len(query_words) > 1:
            query_phrase = original_query.lower()
            if query_phrase in all_repo_text:
                phrase_bonus = 5

        # Stars bonus (popular repos get slight boost)
        stars_bonus = min(repo.get('stargazers_count', 0) / 1000, 2)

        # Language preference bonus (boost repos that match detected project language)
        language_bonus = 0
        if preferred_language:
            repo_language = repo.get('language', '')
            if repo_language and repo_language.lower() == preferred_language.lower():
                language_bonus = 3  # Significant boost for same language
                print(f"🎯 Language match bonus: {repo.get('name')} ({repo_language})")

        # Calculate final score
        raw_score = overlap + name_matches + desc_matches + topic_matches + readme_matches + phrase_bonus + stars_bonus + language_bonus

        # Normalize to 0.00-1.00 range (assuming max possible score around 20)
        max_possible_score = 20  # Approximate maximum for normalization
        normalized_score = min(raw_score / max_possible_score, 1.0)

        return round(normalized_score, 2)

    def search_repositories(self, query, limit=10):
        """Search for repositories using GitHub Search API."""
        search_url = f"{self.base_url}/search/repositories"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 100)
        }

        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            search_data = response.json()

            # Don't fetch READMEs here - will fetch for final results later

            return search_data
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}

    def search_multiple_variations(self, variations, original_query, limit=10, preferred_language=None):
        """Search using multiple query variations and merge results."""
        all_results = []
        seen_repos = set()

        print(f"🔍 Searching with {len(variations)} variations: {variations}")

        # Search with each variation
        for i, variation in enumerate(variations):
            print(f"📡 Search {i+1}: '{variation}'")
            search_data = self.search_repositories(variation, limit=15)  # Get 15 per variation for total ~30-45

            if "error" not in search_data:
                for repo in search_data.get('items', []):
                    repo_id = repo['id']
                    if repo_id not in seen_repos:
                        seen_repos.add(repo_id)
                        # Add semantic relevance score
                        repo['semantic_relevance'] = self.calculate_semantic_relevance(original_query, repo, preferred_language)
                        repo['found_via_query'] = variation
                        all_results.append(repo)

        # Sort by semantic relevance (descending) then by stars
        all_results.sort(key=lambda x: (x['semantic_relevance'], x['stargazers_count']), reverse=True)

        # Limit to requested number
        final_results = all_results[:limit]

        # Now fetch READMEs for the final top results
        print(f"📊 Found {len(all_results)} unique repositories, showing top {len(final_results)}")
        print("📖 Fetching READMEs for top results...")

        for i, repo in enumerate(final_results):
            owner = repo['owner']['login']
            repo_name = repo['name']
            repo['readme_preview'] = self.get_readme_content(owner, repo_name)
            if i < len(final_results) - 1:  # Don't sleep after the last one
                time.sleep(0.2)  # Small delay to avoid rate limiting

        return {
            'total_count': len(all_results),
            'items': final_results
        }


searcher = GitHubWebSearcher()
query_parser = NaturalLanguageQueryParser()
diagram_generator = MermaidDiagramGenerator()


@app.route('/')
def index():
    """Render the main search page."""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    data = request.get_json()
    query = data.get('query', '').strip()
    preferred_language = data.get('preferred_language')

    if not query:
        return jsonify({"error": "Please enter a search query"})

    # Parse natural language query into multiple search variations
    search_variations = query_parser.parse_natural_language_query(query)

    # Log the query transformation
    print(f"🔍 Query transformation: '{query}' → {search_variations}")
    if preferred_language:
        print(f"🎯 Preferred language: {preferred_language}")

    # Search using multiple variations and merge results
    results = searcher.search_multiple_variations(search_variations, query, limit=10, preferred_language=preferred_language)

    if "error" in results:
        return jsonify({"error": results["error"]})

    return jsonify({
        "original_query": query,
        "search_variations": search_variations,
        "total_count": results.get('total_count', 0),
        "repositories": results.get('items', [])
    })


@app.route('/generate-diagram', methods=['POST'])
def generate_diagram():
    """Generate a Mermaid diagram for a repository."""
    data = request.get_json()
    owner = data.get('owner', '').strip()
    repo = data.get('repo', '').strip()

    if not owner or not repo:
        return jsonify({"error": "Owner and repository name are required"})

    # Fetch repository file structure
    tree_data = searcher.get_repository_tree(owner, repo)

    if "error" in tree_data:
        return jsonify({"error": tree_data["error"]})

    # Generate Mermaid diagram
    repository_name = f"{owner}/{repo}"
    files = tree_data.get("files", [])

    if not files:
        return jsonify({"error": "No files found in repository"})

    mermaid_diagram = diagram_generator.generate_mermaid_diagram(repository_name, files)

    return jsonify({
        "repository": repository_name,
        "file_count": len(files),
        "diagram": mermaid_diagram
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)