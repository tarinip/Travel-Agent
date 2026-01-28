# Architecture Audit: Travel Architect 2026

## 1. System Overview

**Project Name:** Travel Architect 2026
**Architecture Pattern:** Event-Driven State Machine (LangGraph) with Human-in-the-Loop (HITL) capabilities.
**Primary Interface:** Web UI (Chainlit).
**Persistence:** PostgreSQL (via `langgraph-checkpoint-postgres`).

The system functions as an autonomous agentic workflow designed to plan travel itineraries. It utilizes a graph-based orchestration engine (LangGraph) to manage complex state transitions between different modes of operation (Planning vs. Quick Lookup). The application is fully asynchronous at the entry level (`app.py`), enabling streaming responses and real-time user feedback.

### Key Control Flow
1.  **Ingestion:** User input is captured via `app.py` (Chainlit).
2.  **Orchestration:** `main.py` initializes the State Graph and routes the input.
3.  **Analysis:** `rewrite.py` classifies the intent (Planner vs. Quick Lookup) and extracts entities.
4.  **Execution:** Depending on the intent, control flows to:
    *   **Planner Path:** `planner.py` -> `deep_research.py` (Recursive Search) -> `synthesizer.py`.
    *   **Quick Path:** `quick_lookup.py` -> `synthesizer.py`.
    *   **Interrupt Path:** If data is missing or unsafe, `human_interruptor.py` halts execution for user input.
5.  **Synthesis:** Results are aggregated and streamed back to the UI.

---

## 2. Component Breakdown

### A. Entry Points & Orchestration
*   **`app.py` (UI Layer):**
    *   **Responsibility:** Manages the Chainlit user session, renders UI elements (status messages, reasoning steps), and streams graph updates.
    *   **Key Logic:** Uses `app.astream()` to consume both "updates" (state transitions) and "messages" (token streaming). Handles the `Command(resume=...)` logic for HITL.
    *   **Dependency:** Directly imports `get_async_app` from `main.py`.

*   **`main.py` (Graph Definition):**
    *   **Responsibility:** Defines the `StateGraph` topology, edges, conditional routing logic (`route_after_rewrite`), and database connection pooling.
    *   **Key Logic:** Configures `AsyncPostgresSaver` for persistence. Contains the critical conditional router that decides between `planner_node`, `quick_lookup_node`, and `human_interrupter_node`.
    *   **Observation:** Currently contains significant amounts of commented-out legacy code (dead code), making maintenance difficult.

### B. Core Nodes (`nodes/`)
*   **`rewrite.py`:**
    *   **Role:** NLU Controller.
    *   **Logic:** Uses OpenAI Structured Outputs to generate a `RewriteNodeOutput` model. Determines safety, completeness, and execution mode.
    *   **Significance:** Acts as the "Guardrail" and "Router" intelligence.

*   **`planner.py`:**
    *   **Role:** Strategy Generator.
    *   **Logic:** Generates search queries based on the user's request.
    *   **Weakness:** Contains hardcoded string templates for booking links (MakeMyTrip, IRCTC), violating separation of concerns.

*   **`deep_research.py`:**
    *   **Role:** Worker Node.
    *   **Logic:** Iterates through the plan, calls `web_search_tool`, and uses an LLM to distill findings.

*   **`quick_lookup.py`:**
    *   **Role:** Fast-path Worker.
    *   **Logic:** Uses DuckDuckGo Instant Answer API for simple fact-retrieval.

*   **`human_interruptor.py`:**
    *   **Role:** Flow Control.
    *   **Logic:** Uses LangGraph's `interrupt` function to suspend the thread until user input is received.

*   **`synthesizer.py`:**
    *   **Role:** Presentation Layer.
    *   **Logic:** Aggregates `research_data` and formats the final markdown response. Adaptive system prompt based on `mode`.

### C. Data & State (`state.py`)
*   **`AgentState` (TypedDict):**
    *   Central data structure containing `messages` (append-only), `user_profile`, `plan`, `research_data`, and routing flags (`is_safe`, `is_incomplete`).
    *   Design is clean and extensible.

### D. Utilities (`utils/`)
*   **`tools.py`:**
    *   Contains `instant_answer_tool` and `web_search_tool`.
    *   **Critical Issue:** Uses the synchronous `requests` library.

---

## 3. Data Flow & State Management

### Data Ingestion
Data enters as `HumanMessage` objects. `rewrite_node` enriches this state by adding structured metadata (`has_kids`, `mode`).

### State Persistence
*   **Mechanism:** `AsyncPostgresSaver` in `main.py`.
*   **Workflow:** Every step of the graph is checkpointed to Postgres. This allows the application to be killed and resumed, or paused for human input, without losing context.
*   **Identifier:** Thread ID is managed in `app.py` (UUID generated on chat start).

### Database Strategy
*   **LangGraph DB:** Managed via `psycopg_pool` in `main.py`. Stores graph checkpoints.
*   **Chainlit DB:** Managed via `SQLAlchemy` in `database.py`. Stores UI-level chat history and user feedback.
*   **Observation:** There is a split strategy here. While functional, having two separate DB connection strategies (Psycopg2 vs SQLAlchemy) adds complexity.

---

## 4. Critical Technical Review

### A. Architectural Pitfalls
1.  **Blocking I/O in Async Application (Critical):**
    *   The application is designed as `async` (`app.py`, `main.py`).
    *   However, `utils/tools.py` uses the synchronous `requests` library.
    *   **Impact:** When a node performs a web search, it **blocks the entire event loop**, freezing the application for all concurrent users until the request completes. This defeats the purpose of using `asyncio`.
2.  **Dead Code Accumulation:**
    *   `main.py` is >50% commented-out code. This creates confusion about the source of truth and increases cognitive load for developers.

### B. Code Quality & Patterns
1.  **Hardcoded Configuration:**
    *   Database URIs are hardcoded in `main.py` (`postgresql://tarinijain@...`). This is a security risk and makes deployment to different environments impossible without code changes.
    *   Hardcoded URLs in `planner.py` for booking links.
2.  **Fragile Web Scraping:**
    *   `web_search_tool` in `utils/tools.py` relies on raw HTML scraping of DuckDuckGo (`html.duckduckgo.com`). This is highly brittle and likely to break if DDG changes their DOM structure or implements stricter rate limiting.

### C. Performance & Security
1.  **Connection Pooling:**
    *   `main.py` initializes a pool with `max_size=20`. Without proper lifecycle management (ensure close on shutdown), this could leak connections in a hot-reload environment like Chainlit.
2.  **Injection Risk:**
    *   While LangChain handles prompt injection to some degree, the `rewrite_node` is the only defense line.

---

## 5. Actionable Recommendations

### Priority 1: Fix Async Blocking
**Refactor `utils/tools.py` to use asynchronous HTTP clients.**
*   Replace `requests` with `aiohttp` or `httpx`.
*   Update `deep_research_node` and `quick_lookup_node` to be `async def` functions to await these calls.

### Priority 2: Code Cleanup & Configuration
**Sanitize `main.py` and Externalize Config.**
*   Remove all commented-out legacy code from `main.py`.
*   Move `DB_URI` and other secrets to environment variables (`os.getenv`).
*   Create a centralized `config.py` to manage these settings.

### Priority 3: Robustness
**Improve Tooling Reliability.**
*   Replace the raw HTML scraper with a proper search API (e.g., Tavily, Serper, or a structured scraping API) to ensure reliability.
*   Implement proper error handling in `web_search_tool` to return graceful degradation messages instead of crashing or returning empty strings.

### Priority 4: Database Unification
**Align Database patterns.**
*   Consider standardizing on one driver or ensuring the `database.py` and `main.py` logic shares configuration to prevent connection limit exhaustion on the Postgres instance.
