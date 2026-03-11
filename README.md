# AI MCP Agent Demo

## Meet Tata Lino 🧟, a not so smart AI Agent

A locally-running AI agent built with **Python** that understands natural-language queries, routes them to the right tools, and responds intelligently — all without relying on a paid API.  
The agent uses **Ollama (llama3.2)** for reasoning, **ChromaDB** for vector memory and knowledge search, and exposes tools through a **FastAPI MCP tool server**.

---

## How It Works

```
User (Streamlit UI)
       │
       ▼
  agent.py  ──── NLP Parser (rule-based + Ollama LLM fallback)
       │
       ├── Fast Router  ──── weather / time / user  (direct tool call)
       │
       ├── Knowledge Search  ──── ChromaDB semantic search (company info)
       │
       ├── Memory Search  ──── ChromaDB short-term conversation memory
       │
       └── Tool Server (FastAPI @ port 8000)
               │
               ├── geocode_location   → Open-Meteo Geocoding API
               ├── get_weather        → Open-Meteo Forecast API
               ├── get_time           → TimeZoneDB API
               ├── get_user           → MariaDB (employee lookup)
               └── search_knowledge   → ChromaDB knowledge collection
```

1. The **Streamlit UI** (`app.py`) sends the user's message to `agent.py`.
2. `agent.py` parses the query with the **NLP parser** (`nlp_parser.py`), which first applies keyword rules (weather, time, user) and falls back to **Ollama llama3.2** for anything complex.
3. The resolved intent is passed to the **fast router** (`router.py`). Known intents are dispatched directly; unknown ones are reasoned over by Ollama using the tool definitions in `config/tools.json`.
4. Tools are executed by calling the **MCP Tool Server** (`main.py` / FastAPI), which auto-discovers and registers all functions in the `tools/` folder via `registry.py`.
5. Before and after each response, the agent searches and saves to **vector memory** (`ChromaDB`) so it can recall earlier conversation context.
6. Company knowledge (from `knowledge/`) is pre-embedded with `build_knowledge.py` and searched semantically to answer questions about the business.

---

## Features

- Natural-language query understanding (rules + Ollama LLM fallback)
- 5-day weather forecast via Open-Meteo (no API key needed)
- Current local time lookup via TimeZoneDB
- Employee/user lookup from MariaDB
- Semantic knowledge base search (ChromaDB + sentence-transformers)
- Short-term vector memory for conversational context
- Auto-discovery tool registry — drop a file in `tools/` and it's live
- Streamlit chat UI with formatted cards for each response type
- Offline rule-based fallback agent (`offline_agent.py`)

---

## Tech Stack

| Layer              | Technology                                 |
| ------------------ | ------------------------------------------ |
| UI                 | Streamlit                                  |
| Agent & routing    | Python 3.10+                               |
| LLM reasoning      | Ollama (llama3.2)                          |
| Tool server        | FastAPI + Uvicorn                          |
| Vector DB / memory | ChromaDB                                   |
| Embeddings         | sentence-transformers (`all-MiniLM-L6-v2`) |
| Database           | MariaDB                                    |
| Weather API        | Open-Meteo (free, no key)                  |
| Geocoding          | Open-Meteo Geocoding API                   |
| Timezone           | TimeZoneDB API                             |

---

## Project Structure

```
ai-mcp-agent-demo/
├── agent.py            # Core agent logic (parse → route → tool → respond)
├── app.py              # Streamlit chat UI
├── main.py             # FastAPI MCP tool server
├── registry.py         # Auto-discovers and registers tools from tools/
├── router.py           # Keyword-based intent router
├── offline_agent.py    # Rule-based fallback (no LLM required)
├── build_knowledge.py  # Embeds knowledge/ docs into ChromaDB
├── requirements.txt
├── config/
│   ├── tools.json      # Tool definitions (name, description, parameters)
│   └── db_mapper.py    # Database connection factory
├── db/
│   └── chroma_client.py
├── knowledge/          # Plain-text documents indexed into ChromaDB
│   ├── company.txt
│   └── services.txt
├── schemas/
│   └── tool_request.py # Pydantic request schema for /tool endpoint
├── tools/
│   ├── geocode_location.py
│   ├── get_weather.py
│   ├── time_tool.py
│   ├── user.py
│   ├── knowledge_search.py
│   └── memory.py
└── vector_db/          # ChromaDB persistent storage
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama and pull the model (required for local LLM)

Install **Ollama** on your machine.

- Download: https://ollama.com/download
- **Windows:** download and run the Ollama Windows installer.
- **macOS/Linux:** install Ollama using the platform instructions on the download page.

Then pull the model used by this project:

```bash
ollama pull llama3.2
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
TIMEZONEDB_API_KEY=your_timezonedb_key
```

### 4. Build the knowledge base

```bash
py build_knowledge.py
```

### 5. Start the MCP tool server

```bash
uvicorn main:app --reload
```

### 6. Run the Streamlit UI

```bash
streamlit run app.py
```

---

## Available Tools

| Tool                            | Description                                               |
| ------------------------------- | --------------------------------------------------------- |
| `geocode_location`              | Converts a city name to latitude, longitude, and timezone |
| `get_weather`                   | Returns a 5-day forecast from Open-Meteo                  |
| `get_time`                      | Returns the current local time for a timezone             |
| `get_user`                      | Looks up an employee by name from MariaDB                 |
| `search_knowledge`              | Semantic search over the company knowledge base           |
| `save_memory` / `search_memory` | Persist and retrieve conversational context               |

---

## Adding a New Tool

1. Create a new `.py` file inside `tools/`.
2. Define a function with a docstring (used as the tool description).
3. Add the tool's JSON definition to `config/tools.json`.
4. Restart the tool server — `registry.py` auto-discovers it.
