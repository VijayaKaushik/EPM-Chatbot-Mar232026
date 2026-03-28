# Visual Architecture Diagrams

## System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                         USER INTERFACE                               ║
║                    (Browser / Mobile App)                            ║
║                   Sends: "Show vesting dates"                        ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │ HTTP POST /chat/sse
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║                      API LAYER (app/api/)                            ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │ chat.py: @router.post("/sse")                               │  ║
║  │ - Receives HTTP request                                      │  ║
║  │ - Extracts: user_msg, session_id, user_id                    │  ║
║  │ - Calls: chat_service.exec_chat_sse()                        │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │ Passes ChatRequest
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║                   SERVICE LAYER (app/service/)                       ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │ chat_service.py: exec_chat_sse()                             │  ║
║  │ - Validates input                                            │  ║
║  │ - Calls: runner_service.run_query_sse()                      │  ║
║  │ - Formats response as SSE                                    │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │ runner_service.py: run_query_sse()                           │  ║
║  │ - Converts message to AI format                              │  ║
║  │ - Creates Runner instance                                    │  ║
║  │ - Calls: runner.run()                                        │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │ Passes to Agent Manager
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║               AGENT MANAGER (app/agent/manager/)                     ║
║  ┌──────────────────────────────────────────────────────────────┐  ║
║  │ agent.py: manager_agent (LlmAgent)                           │  ║
║  │ - Receives: "Show vesting dates"                             │  ║
║  │ - Analyzes query                                             │  ║
║  │ - Decides: "This is a vesting question"                      │  ║
║  │ - Routes to: vesting_agent                                   │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │ Routes to specialist
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║         SPECIALIST AGENTS (app/agent/manager/sub_agent/)             ║
║                                                                      ║
║  ┌─── VESTING AGENT ────────────────────────────────────────────┐  ║
║  │ agent.py: vesting_agent (LlmAgent)                           │  ║
║  │ - Reads query: "Show vesting dates"                          │  ║
║  │ - Checks skills: vesting_schedule/SKILL.md                   │  ║
║  │ - Determines tools needed: get_vesting_dates()               │  ║
║  │ - Calls: get_vesting_dates(month=5, year=2026)               │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                            ↓
║  ┌─── VESTING TOOLS ────────────────────────────────────────────┐  ║
║  │ tool.py functions:                                           │  ║
║  │ • get_vesting_dates() → Loads vesting_dates.csv              │  ║
║  │ • get_vesting_details() → Loads vesting_details/*.csv        │  ║
║  │ • calculate_tax() → Processes financial data                 │  ║
║  │ • filter_participants() → Filters by criteria                │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                            ↓
║  ┌─── DATA LOADING ─────────────────────────────────────────────┐  ║
║  │ vesting_data/ folder:                                        │  ║
║  │ ├── vesting_dates.csv (Calendar)                             │  ║
║  │ │   CLIENT_001, 2026-05-15                                   │  ║
║  │ │   CLIENT_001, 2026-05-20                                   │  ║
║  │ │   CLIENT_001, 2026-05-25                                   │  ║
║  │ │   ...                                                      │  ║
║  │ └── vesting_details/ (Participant data)                      │  ║
║  │     ├── 2026-05-15.csv                                       │  ║
║  │     ├── 2026-05-20.csv                                       │  ║
║  │     └── 2026-05-25.csv                                       │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
║                            ↓
║  ┌─── TOOL RESPONSE ────────────────────────────────────────────┐  ║
║  │ Returns: {                                                   │  ║
║  │   "status": "success",                                       │  ║
║  │   "vesting_dates": [                                         │  ║
║  │     "2026-05-15",                                            │  ║
║  │     "2026-05-20",                                            │  ║
║  │     "2026-05-25"                                             │  ║
║  │   ]                                                          │  ║
║  │ }                                                            │  ║
║  └──────────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │ Agent formats response
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║               AGENT MANAGER (Returns Response)                       ║
║  - Receives tool output                                              ║
║  - Formats: "Found 3 vesting dates in May 2026:..."                 ║
║  - Sends back through layers                                         ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║                   SERVICE LAYER (Response Path)                      ║
║  - Formats as Server-Sent Events (SSE)                               ║
║  - Creates streaming response                                        ║
╚═══════════════════════════╤════════════════════════════════════════╝
                            │ Streaming Response
                            ↓
╔══════════════════════════════════════════════════════════════════════╗
║                         USER INTERFACE                               ║
║                   Display: "Found 3 dates:"                          ║
║                           - May 15, 2026                             ║
║                           - May 20, 2026                             ║
║                           - May 25, 2026                             ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Data Flow Diagram

```
┌─────────────────┐
│  USER MESSAGE   │
│ "Show vesting"  │
└────────┬────────┘
         │
         ↓ (ChatRequest object)
┌────────────────────────────────┐
│  REQUEST OBJECT (Models)       │
│ {                              │
│   user_msg: "...",             │
│   session_id: "abc123",        │
│   user_id: "user@company"      │
│ }                              │
└────────┬────────────────────────┘
         │
         ↓ (Validation & Preparation)
┌────────────────────────────────┐
│  AI CONTENT OBJECT             │
│ {                              │
│   role: "user",                │
│   parts: [text: "..."]         │
│ }                              │
└────────┬────────────────────────┘
         │
         ↓ (Processing)
┌────────────────────────────────┐
│  MANAGER AGENT DECISION        │
│ Routes to: vesting_agent       │
└────────┬────────────────────────┘
         │
         ↓ (Specialized Processing)
┌────────────────────────────────┐
│  VESTING AGENT PROCESSING      │
│ Calls: get_vesting_dates()     │
└────────┬────────────────────────┘
         │
         ↓ (Data Access)
┌────────────────────────────────┐
│  LOAD FROM CSV                 │
│ vesting_data/vesting_dates.csv │
└────────┬────────────────────────┘
         │
         ↓ (Filtering)
┌────────────────────────────────┐
│  FILTER RESULTS                │
│ month == 5 AND year == 2026    │
└────────┬────────────────────────┘
         │
         ↓ (Tool Response)
┌────────────────────────────────┐
│  TOOL OUTPUT                   │
│ {                              │
│   status: "success",           │
│   vesting_dates: [...]         │
│ }                              │
└────────┬────────────────────────┘
         │
         ↓ (Formatting)
┌────────────────────────────────┐
│  LLM FORMATTED RESPONSE        │
│ "Found 3 dates: ..."           │
└────────┬────────────────────────┘
         │
         ↓ (Streaming)
┌────────────────────────────────┐
│  SERVER-SENT EVENTS            │
│ data: {...}\n\n                │
│ data: {...}\n\n                │
└────────┬────────────────────────┘
         │
         ↓ (Display)
┌────────────────────────────────┐
│  USER SEES RESPONSE            │
│ Browser/App shows the answer   │
└────────────────────────────────┘
```

---

## Folder Structure with Code Responsibilities

```
epm-chatbot/
│
├── app/                          # MAIN APPLICATION CODE
│   │
│   ├── main.py                   # 🚪 ENTRY POINT
│   │   └─ Creates FastAPI app
│   │   └─ Registers all route handlers
│   │
│   ├── api/                      # 📡 API LAYER (External Communication)
│   │   ├── chat.py              # Handles /chat endpoints
│   │   │   └─ POST /chat → exec_chat()
│   │   │   └─ POST /chat/sse → exec_chat_sse()
│   │   │   └─ GET /chat/history → get_chat_history()
│   │   │
│   │   ├── session.py           # Handles session management
│   │   ├── prompt.py            # Direct LLM prompts
│   │   └── learning_sse.py      # Learning module
│   │
│   ├── models/                   # 📦 DATA STRUCTURES (What data looks like)
│   │   ├── chat_request.py      # Input format
│   │   │   └─ ChatRequest {user_msg, session_id, user_id}
│   │   │
│   │   ├── chat_history.py      # Response format
│   │   │   └─ ChatMessage {role, message}
│   │   │
│   │   └── ... other models
│   │
│   ├── service/                  # ⚙️ SERVICE LAYER (Business Logic)
│   │   ├── chat_service.py      # Main chat processor
│   │   │   ├─ exec_chat()      → processes one query
│   │   │   ├─ exec_chat_sse()  → streams response
│   │   │   └─ get_all_messages()→ retrieves history
│   │   │
│   │   └── ai_workflow/         # AI Execution Engine
│   │       ├── runner_service.py# Runs agents
│   │       │   ├─ run_query() → Execute once
│   │       │   └─ run_query_sse()→ Stream response
│   │       │
│   │       ├── db_session_service.py # Session persistence
│   │       │   └─ Stores/retrieves chat history
│   │       │
│   │       └── session_service.py# Alternative (in-memory)
│   │
│   ├── db/                       # 💾 DATABASE LAYER
│   │   ├── prompt_repository.py # Access prompts
│   │   └── user_activity_history_repository.py
│   │
│   └── agent/                    # 🧠 AI AGENTS
│       └── manager/
│           ├── agent.py         # Manager Agent
│           │   └─ Routes to sub-agents
│           │
│           ├── utils.py         # Helper functions
│           └── sub_agent/       # Specialist Agents
│               │
│               ├── vesting_agent/      # 🎯 VESTING SPECIALIST
│               │   ├── agent.py        # Vesting agent definition
│               │   ├── tool.py         # Functions:
│               │   │   ├─ get_vesting_dates()
│               │   │   ├─ get_vesting_details()
│               │   │   ├─ calculate_tax()
│               │   │   └─ filter_participants()
│               │   │
│               │   ├── utils.py
│               │   ├── skills/         # Workflows
│               │   │   ├── vesting_schedule/SKILL.md
│               │   │   └── release_workflow/SKILL.md
│               │   │
│               │   └── vesting_data/   # 📊 DATA
│               │       ├── vesting_dates.csv         (Calendars)
│               │       └── vesting_details/          (Employee data)
│               │           ├── 2026-05-15.csv
│               │           ├── 2026-05-20.csv
│               │           └── ... more dates
│               │
│               ├── releasemanagement_agent/  # 📋 RELEASE SPECIALIST
│               │   ├── agent.py
│               │   ├── tool.py
│               │   └── skills/
│               │
│               └── old_agents/              # 📦 ARCHIVE
│                   ├── data_analysis_agent/
│                   ├── knowledge_base_agent/
│                   └── reporting_agent/
│
├── pyproject.toml                # 📝 PROJECT CONFIG
│   └─ Dependencies list
│   └─ Python version
│
└── *.db files                    # 💾 DATABASES
    ├── my_agent_data.db         (Chat history)
    └── user_activity.db         (User actions)
```

---

## Request Processing Pipeline

```
REQUEST ENTERS SYSTEM
        │
        ↓
╔═══════════════════════════╗
║ API LAYER                 ║  ← Handles HTTP
║ /chat/sse receives POST   ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ SERVICE LAYER             ║  ← Prepares data
║ exec_chat_sse()           ║
║ • Validates request       ║
║ • Builds AI message       ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ RUNNER                    ║  ← Manages execution
║ runner.run()              ║
║ • Gets session history    ║
║ • Passes to manager agent ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ MANAGER AGENT             ║  ← Makes decision
║ Analyzes query            ║
║ Selects sub-agent         ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ SPECIALIST AGENT          ║  ← Executes task
║ (e.g., vesting_agent)     ║
║ • Reads skills            ║
║ • Calls tools             ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ TOOL EXECUTION            ║  ← Does work
║ • Loads data              ║
║ • Processes information   ║
║ • Returns result          ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ AGENT FORMATTING          ║  ← Prepares response
║ Converts to natural text  ║
╚═══════════════════════════╝
        │
        ↓
╔═══════════════════════════╗
║ RESPONSE STREAMING        ║  ← Sends to user
║ SSE formatted             ║
║ Back through layers       ║
╚═══════════════════════════╝
        │
        ↓
RESPONSE REACHES USER
(Browser/App displays)
```

---

## Memory & Session Flow

```
┌────────────────────────────────────────┐
│ USER 1: "Show vesting dates"           │
│ Session: "session-abc123"              │
└────────────────────────────────────────┘
         │
         ↓ (Stored in Database)
┌────────────────────────────────────────┐
│ my_agent_data.db                       │
│ ┌──────────────────────────────────┐  │
│ │ SESSION: session-abc123          │  │
│ │ ├─ User: user@company.com        │  │
│ │ ├─ Message 1: "Show vesting..."  │  │
│ │ ├─ Response 1: "Found 3 dates..."│  │
│ │ └─ Timestamp: 2026-03-25 10:00   │  │
│ └──────────────────────────────────┘  │
└────────────────────────────────────────┘
         │
         ↓ (Later, same user)
┌────────────────────────────────────────┐
│ USER 1 (5 mins later):                 │
│ "Show details for May 15"              │
│ Same Session: "session-abc123"         │
└────────────────────────────────────────┘
         │
         ↓ (Runner retrieves history)
┌────────────────────────────────────────┐
│ AGENT SEES CONTEXT:                    │
│ "Previously asked about vesting..."    │
│ "Now asking for details..."            │
│ "Can use previous context!"            │
└────────────────────────────────────────┘
         │
         ↓ (Generates smarter response)
┌────────────────────────────────────────┐
│ RESPONSE:                              │
│ "Here are details for May 15..."       │
│ (More contextual & relevant)           │
└────────────────────────────────────────┘
```
