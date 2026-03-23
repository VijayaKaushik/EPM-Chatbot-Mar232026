# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About This Project

An AI agent system built with Google ADK (Agent Development Kit) for managing equity compensation plans (RSUs, PSUs, Stock Options). A central manager agent classifies user intent and routes to specialist sub-agents. Sub-agents use skills (SKILL.md files) to guide workflows.

**Tech stack**: Python 3.14, Google ADK (from git main), FastAPI + Uvicorn, uv package manager, Gemini API, PandasAI for data analysis.

## Key Commands

```bash
uv sync                                          # Install dependencies
uv add <package>                                  # Add package (never pip install)
uv run uvicorn app.main:app --reload              # Run FastAPI server
adk web app/agent/manager                         # Run ADK web UI (from project root)
uv run pytest tests/ -v                           # Run tests
uv run ruff check .                               # Lint
uv run ruff format .                              # Format
```

Always prefix Python commands with `uv run`.

## Architecture

### Request flow
1. Client → FastAPI (`app/main.py`) → route handlers in `app/api/`
2. `POST /chat/sse` → `chat_service.exec_chat_sse()` → `runner_service.run_query_sse()`
3. Runner (ADK) dispatches to `manager_agent` → routes to sub-agents
4. Sessions persisted via ADK `DatabaseSessionService` (SQLite: `my_agent_data.db`)

### Agent hierarchy
- **Manager agent** (`app/agent/manager/agent.py`): `manager_agent` — routes to sub-agents using `gemini-2.5-flash` (via `utils.get_model()`, which has LiteLLM/Ollama support commented out)
- **Active sub-agent**: `releasemanagement_agent` (`app/agent/manager/sub_agent/releasemanagement_agent/`) — handles vesting, tax, data analysis
- **Old/archived agents**: `app/agent/manager/sub_agent/old_agents/` — data_analysis, knowledge_base, release, reporting, release_management_langgraph, release_management_withfilters

### Sub-agent pattern
Each sub-agent has: `agent.py` (LlmAgent definition), `tool.py` (all tools in one file), `skills/` folder with `SKILL.md` files loaded via `load_skill_from_dir()` + `SkillToolset`.

### Session & state
- **app_name**: `"GoogleADK"` — must be consistent across all services
- `DatabaseSessionService` in `app/service/ai_workflow/db_session_service.py` (SQLite, **not** aiosqlite — uses `sqlite:///`)
- `InMemorySessionService` alternative in `session_service.py` (swappable)
- `tool_context.state["token_vesting_list"]` stores `List[Tuple[vesting_date, token_id]]` — set by `get_vesting_details`, consumed by `calculate_tax`

### API routes
| Route | Handler |
|---|---|
| `POST /session` | `app/api/session.py` |
| `POST /chat`, `POST /chat/sse`, `GET /chat/history` | `app/api/chat.py` |
| `POST /prompt` | `app/api/prompt.py` |
| Learning SSE | `app/api/learning_sse.py` |
| User activity history | `app/api/user_activity_history.py` |

## ADK Conventions

- Skills must have `name` and `description` in YAML frontmatter — `description` drives ADK semantic skill matching
- Tools referenced in a skill's SKILL.md must exist in the agent's `tool.py`
- Never expose `token_id` or internal state keys to users
- Always validate tool preconditions (e.g., token must exist before `calculate_tax`)
- `analyze_release_data` uses PandasAI with a Faker-generated 100-row DataFrame (seeded, deterministic)

## Git Workflow

- **Never commit to `main` directly** — use feature branches
- **Never commit `.env`**
- Branch naming: `feat/`, `fix/`, `chore/`
- Conventional commits: `feat:`, `fix:`, `chore:`
- Run tests before pushing

## progress.md (Required)

After every completed task, append an entry to `progress.md` (project root, committed to git):

```
---
### [YYYY-MM-DD HH:MM EST] <Short title>

**What changed**
- List each file created or modified

**Logic & data flow**
How data moves, what triggers what, why this approach.

**Assumptions**
- Decisions made without explicit requirement

**Context for future contributors**
What a new developer must know that isn't obvious from code.
---
```

Rules: timestamps in US/Eastern, append only, never skip an entry, write entries yourself.

## Important Constraints

- `adk web` must point to `app/agent/manager` (not orchestrator)
- Ask before any structural changes to `app/agent/` or `app/service/`
- When adding a new tool, reference it in the relevant SKILL.md workflow
- google-adk is installed from git main branch (not PyPI)
