# End-to-End Architecture Guide - Learning Resource

## High-Level Overview

This is an **AI Agent System** that processes user questions and routes them to specialized agents. Think of it like a customer service center where a manager routes calls to different departments.

```
User Question → API → Service Layer → Agent Manager → Specialist Agents → Response
```

---

## 🌐 Part 1: The Front Door (API Layer)

### Location: `/app/api/`

**What it does**: Receives HTTP requests from clients (web/mobile apps)

#### Key Files:
- **`chat.py`** - Main chat endpoint
  - `POST /chat` - Send a user message
  - `POST /chat/sse` - Send a message with real-time streaming
  - `GET /chat/history` - Get past conversations
  
- **`session.py`** - Manage user sessions
- **`prompt.py`** - Direct LLM prompts
- **`learning_sse.py`** - Learning module
- **`user_activity_history.py`** - Track user actions

### Example Flow:
```
User sends: "Show me vesting dates for May"
                    ↓
Browser sends HTTP POST to: `/chat/sse`
Request body: {
    "user_msg": "Show me vesting dates for May",
    "session_id": "abc123",
    "user_id": "user@company.com"
}
                    ↓
API receives and processes
```

---

## 🚀 Part 2: The Service Layer (Business Logic)

### Location: `/app/service/`

**What it does**: Takes the user request and prepares it for the AI system

#### Key Files:

**`chat_service.py`** - Main chat processor
```python
def exec_chat_sse(request: ChatRequest):
    # Takes user message
    # Calls runner to process through agents
    # Returns streaming response
    for ai_response in run_query_sse(...):
        yield response
```

**`ai_workflow/runner_service.py`** - Brain of the system
```python
runner = Runner(
    agent=manager_agent,           # Which agent to use
    session_service=session_service, # Where to store chat history
    app_name="GoogleADK"           # App name
)

def run_query_sse(query, session_id, user_id):
    # Calls the agent with the query
    # Streams back responses
```

### What happens here:
1. User message arrives from API
2. Service layer validates it
3. Creates a content object for the AI
4. Sends to Runner with session info
5. Runner manages conversation history

---

## 🧠 Part 3: The AI Agent System (Google ADK)

### Location: `/app/agent/`

**What it does**: Makes intelligent decisions about what to do with user questions

### Manager Agent
**Location**: `/app/agent/manager/agent.py`

```python
manager_agent = LlmAgent(
    name="Manager",
    model="gemini-2.5-flash",  # Uses Google's AI model
    instruction="Routes tasks to sub agents",
    sub_agents=[
        reporting_agent,
        knowledge_base_agent,
        data_analysis_agent
    ]
)
```

**The Manager's Job**:
- Reads the user question
- Decides which specialist agent should handle it
- Routes the request to that specialist
- Collects the response
- Returns it to the user

Example:
```
User: "Show vesting dates"
Manager thinks: "This is a vesting question" 
→ Routes to vesting_agent
↓
vesting_agent processes it
↓
Manager gets result and returns to user
```

### Specialist Agents (Sub-agents)
**Location**: `/app/agent/manager/sub_agent/`

Each sub-agent is specialized in one area:

1. **`vesting_agent/`** - Handles vesting-related queries
   - Shows vesting dates
   - Retrieves participant details
   - Calculates taxes
   - Manages releases

2. **`releasemanagement_agent/`** - Handles equity release processes
   - Creates release batches
   - Applies filters
   - Processes tax calculations

3. **`old_agents/`** - Legacy agents (archived for reference)
   - data_analysis_agent
   - knowledge_base_agent
   - reporting_agent

---

## 🔧 Part 4: How a Specialist Agent Works

### Example: vesting_agent

**Location**: `/app/agent/manager/sub_agent/vesting_agent/`

### Structure:
```
vesting_agent/
├── agent.py          # Agent definition
├── tool.py           # Functions (tools) agent can call
├── utils.py          # Helper functions
├── skills/           # Workflows (how to handle user requests)
│   ├── vesting_schedule/SKILL.md
│   └── release_workflow/SKILL.md
└── vesting_data/     # Data files (CSVs)
    ├── vesting_dates.csv
    └── vesting_details/
        ├── 2026-05-15.csv
        ├── 2026-05-20.csv
        └── ... more dates
```

### How it works:

#### 1. **agent.py** - Define the agent
```python
vesting_agent = LlmAgent(
    name="VestingAgent",
    model="gemini-2.5-flash",
    tools=[
        get_vesting_dates,      # Can call this function
        get_vesting_details,    # Can call this function
        calculate_tax,          # Can call this function
    ]
)
```

#### 2. **tool.py** - Define tools (functions agent can call)
```python
def get_vesting_dates(client_id, count=None, month=None):
    """
    When user asks: "Show me next 3 vesting dates"
    The agent calls this function
    """
    # Loads vesting_dates.csv
    # Filters by parameters
    # Returns dates
    
def get_vesting_details(vesting_date):
    """
    When user asks: "Show details for May 15"
    The agent calls this function
    """
    # Loads 2026-05-15.csv
    # Returns employee data
```

#### 3. **skills/SKILL.md** - Define workflows
```yaml
name: vesting-schedule
description: View vesting dates and participant details
```

Tells the agent:
- What user questions to handle
- Which tools to use
- In what order

### 4. **vesting_data/** - Store data
- `vesting_dates.csv` - Calendar of all vesting dates
- `vesting_details/*.csv` - Employee data for each date

---

## 📊 Part 5: Data Layer

### Location: `/app/db/` and `/app/models/`

**What it does**: Stores and manages data

### Models (Data Structures)
**Location**: `/app/models/`

```python
# chat_request.py
class ChatRequest:
    user_msg: str          # The user's question
    session_id: str        # Unique session ID
    user_id: str          # Who is asking

# chat_history.py
class ChatMessage:
    role: str              # "user" or "assistant"
    message: str           # The actual message
```

### Database
**Location**: `/app/db/`

- Stores chat history
- Stores user activity
- Session management

**Files**: `*.db` (SQLite databases)
- `my_agent_data.db` - Chat history
- `user_activity.db` - User actions

---

## 🔄 Complete End-to-End Flow

### Scenario: User asks "Show me vesting dates for May 2026"

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CLIENT (Browser/App)                                          │
│    User types: "Show me vesting dates for May 2026"             │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│ 2. API LAYER (/app/api/chat.py)                                 │
│    @router.post("/sse")                                          │
│    Function: chat_sse(request: ChatRequest)                      │
│    - Receives user message                                       │
│    - Calls exec_chat_sse(request)                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. SERVICE LAYER (/app/service/chat_service.py)                 │
│    Function: exec_chat_sse(request)                              │
│    - Validates request                                           │
│    - Calls run_query_sse()                                       │
│    - Formats response as streaming data                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. RUNNER (/app/service/ai_workflow/runner_service.py)          │
│    Function: run_query_sse(query, session_id, user_id)          │
│    - Converts message to AI format                               │
│    - Calls runner.run()                                          │
│    - Manages session history                                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. MANAGER AGENT (/app/agent/manager/agent.py)                  │
│    manager_agent (Google ADK LlmAgent)                           │
│    - Receives: "Show me vesting dates for May 2026"              │
│    - Thinks: "This is about vesting"                             │
│    - Routes to: vesting_agent                                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. VESTING AGENT (/app/agent/manager/sub_agent/vesting_agent/)  │
│    vesting_agent (Google ADK LlmAgent)                           │
│    - Reads user query                                            │
│    - Reads skills: vesting_schedule/SKILL.md                     │
│    - Knows it should call: get_vesting_dates()                   │
│    - Calls: get_vesting_dates(month=5, year=2026)                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. VESTING TOOLS (/app/agent/manager/sub_agent/vesting_agent/)  │
│    tool.py → get_vesting_dates()                                 │
│    - Loads: vesting_data/vesting_dates.csv                       │
│    - Filters: month=5, year=2026                                 │
│    - Finds: [2026-05-15, 2026-05-20, 2026-05-25]                │
│    - Returns: {"status": "success", "vesting_dates": [...]}      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. VESTING AGENT (Processing result)                             │
│    - Receives tool response                                      │
│    - Formats: "Found 3 vesting dates in May 2026:..."           │
│    - Sends response back                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. MANAGER AGENT                                                 │
│    - Receives vesting_agent response                             │
│    - Returns to user                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. RUNNER                                                       │
│     - Packs response                                             │
│     - Saves to session history                                   │
│     - Yields to service layer                                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 11. SERVICE LAYER                                                │
│     - Formats as SSE (Server-Sent Events)                        │
│     - Streams to client                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Streaming Response
┌─────────────────────────────────────────────────────────────────┐
│ 12. CLIENT (Browser displays)                                    │
│     "Found 3 vesting dates in May 2026:                          │
│      - May 15, 2026                                              │
│      - May 20, 2026                                              │
│      - May 25, 2026"                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Roles Summary Table

| Folder | Role | Key Files | What Happens Here |
|--------|------|-----------|-------------------|
| `/api/` | Entry Point | `chat.py`, `session.py` | Receives HTTP requests |
| `/service/` | Business Logic | `chat_service.py`, `runner_service.py` | Prepares requests for AI |
| `/agent/manager/` | Coordinator | `agent.py` | Routes to specialist agents |
| `/agent/manager/sub_agent/vesting_agent/` | Specialist | `agent.py`, `tool.py`, `skills/` | Handles vesting questions |
| `/agent/manager/sub_agent/vesting_agent/vesting_data/` | Data Store | `.csv` files | Stores vesting information |
| `/models/` | Data Structures | `chat_request.py`, etc. | Defines data formats |
| `/db/` | Database Access | `.py` files | Reads/writes to SQLite |

---

## 🎯 Key Learning Concepts

### 1. **Layered Architecture**
```
┌─────────────────┐
│  UI/Client      │  ← User interacts here
├─────────────────┤
│  API Layer      │  ← Receives requests
├─────────────────┤
│  Service Layer  │  ← Processes requests
├─────────────────┤
│  Agent Layer    │  ← Makes AI decisions
├─────────────────┤
│  Data Layer     │  ← Stores data
└─────────────────┘
```

### 2. **Request-Response Cycle**
- Every user action starts as a request
- Each layer processes and passes to next layer
- Finally sends response back through all layers

### 3. **Separation of Concerns**
Each folder has ONE main job:
- API: Accept requests
- Service: Prepare data
- Agent: Make decisions
- Data: Store/retrieve

### 4. **Tools vs Skills vs Agent**
- **Agent**: The "brain" that makes decisions
- **Skills**: Tells the brain what it CAN do
- **Tools**: The actual functions it calls

### 5. **Streaming vs Traditional Response**
- **Traditional**: Waits for complete answer, then returns
- **Streaming** (SSE): Sends answer piece-by-piece in real-time

---

## 💡 Tips for Learning

1. **Start with simple request**: Follow `/api/chat.py` → `/service/` → `/agent/`
2. **Understand the data**: Look at `.csv` files and `.db` files
3. **Trace one example**: Pick a user question and follow it through all layers
4. **Read the skills**: `/agent/manager/sub_agent/vesting_agent/skills/` explain workflows
5. **Experiment**: Try modifying a tool and see how it affects the response

---

## 🔍 Advanced: Session Management

**Sessions keep track of conversation context**

```python
# When user sends message:
runner.run(
    user_id="user@company.com",      # WHO is asking
    session_id="session-abc123",      # WHICH conversation
    new_message=message               # WHAT they're saying
)

# Runner saves in database:
# "user@company.com" in "session-abc123" said: "Show me vesting dates"
# Agent responded: "Found 3 dates..."

# Next time user asks in same session:
# Agent can remember context from before!
```

---

## 📚 Next Steps to Learn More

1. **Understand Google ADK**: Read how `LlmAgent` works
2. **Learn about Tools**: How `tool.py` defines callable functions
3. **Explore Skills**: How `SKILL.md` files work
4. **Database**: How chat history is stored and retrieved
5. **Streaming**: How Server-Sent Events work

---

## Questions to Ask Yourself

- **What happens if a user sends an empty message?**
- **How does the system remember previous conversations?**
- **What if multiple agents could handle the same question?**
- **How are permissions/roles managed?**
- **What if an agent crashes?**
- **How is the AI model chosen?**

These questions will help you understand system design better!
