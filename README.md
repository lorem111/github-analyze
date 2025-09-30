# reCode - great artists ~~steal~~ repurpose code

Search GitHub repositories with natural language and generate architecture diagrams

Built at the **Fullstack Agents Hackathon** at Microsoft SV Center

## 🚀 Features

- **Natural Language Search**: Use plain English to find GitHub repositories
- **AI-Powered Query Optimization**: Automatically generates 3 search variations using Gemini 2.5 Flash
- **Semantic Relevance Scoring**: Smart ranking based on query matching (0.00-1.00 scale)
- **README Previews**: View repository descriptions and README content
- **Language-Aware Search**: Upload project files to boost results in matching languages
- **Architecture Diagram Generation**: AI-generated Mermaid diagrams showing repository structure
- **Interactive UI**: Clean, responsive web interface with modal diagrams

## 🛠 Technology Stack

- **Backend**: Flask, Python 3.8+
- **AI/LLM**: OpenRouter API with Gemini 2.5 Flash
- **APIs**: GitHub REST API and Search API
- **Frontend**: HTML, CSS, JavaScript, Mermaid.js
- **Environment**: python-dotenv for configuration

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd github-analyze
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   - `OPENROUTER_API_KEY`: Get from [OpenRouter](https://openrouter.ai/)
   - `GITHUB_TOKEN`: Get from [GitHub Settings](https://github.com/settings/tokens) (requires `public_repo` permission)

## 🚀 Usage

### Web Application
```bash
python3 web_app.py
```
Visit http://localhost:5001

### Command Line Tools

**Search repositories:**
```bash
python3 github_search.py --search "machine learning"
```

**Analyze specific repository:**
```bash
python3 github_analyzer.py https://github.com/owner/repo
```

## 💡 How It Works

1. **Smart Search**: Enter natural language queries like "bird song detection" or "web scraping tool"
2. **AI Processing**: Gemini 2.5 Flash generates multiple search variations for comprehensive results
3. **Semantic Ranking**: Results ranked by relevance to your original query
4. **Language Matching**: Upload a project file to prioritize repositories in the same language
5. **Architecture Visualization**: Generate Mermaid diagrams showing repository structure and relationships

## 🏆 Hackathon Project

Created at the **Fullstack Agents Hackathon** at Microsoft SV Center

**Event Details:**
- Hosted by B Capital, CopilotKit, LlamaIndex, Composio, and Microsoft for Startups
- $20,000+ in prizes with 300+ fellow builders
- One-day hackathon focused on building fullstack AI agents

**Sponsors:**
- **B Capital** — Global investment firm with $9B+ AUM
- **CopilotKit** — Open-source React framework for fullstack AI agents
- **LlamaIndex** — Framework for connecting LLMs to data
- **Composio** — Action layer for agents with 100+ integrations
- **Microsoft for Startups** — Credits, technical guidance, and go-to-market support

## 🔧 Project Structure

```
github-analyze/
├── web_app.py              # Main Flask application
├── github_search.py        # CLI search tool
├── github_analyzer.py      # Repository analysis tool
├── templates/
│   └── index.html          # Web interface
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 📝 API Endpoints

- `GET /` - Main web interface
- `POST /search` - Repository search with natural language processing
- `POST /generate-diagram` - Generate Mermaid architecture diagrams

## 🌟 Key Features in Detail

### Natural Language Processing
Uses Gemini 2.5 Flash to transform queries like "I want to find a solution to detect bird sound" into optimized search terms: "bird detection", "audio classification", "sound recognition"

### Semantic Relevance Scoring
Calculates relevance based on:
- Repository name matches (highest weight)
- Description matches
- Topic/tag matches
- README content matches
- Language preference bonuses
- Popularity (stars) bonus

### Architecture Diagrams
AI-generated Mermaid flowcharts showing:
- Main directories and structure
- Important files and their relationships
- Project architecture and dependencies
- Clean, readable visual representation

## 🤝 Contributing

Feel free to submit issues and pull requests to improve reCode!

## 📄 License

This project was created for the Fullstack Agents Hackathon. Please check with the original authors for licensing terms.