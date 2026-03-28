# Vesting Agent - Deep Dive Learning Guide

This is a detailed explanation of how the **vesting_agent** works. It's the most complete agent in your system and a great example to learn from.

---

## What Does the Vesting Agent Do?

**Purpose**: Handles all questions about employee equity vesting

**Examples of what it handles**:
- "Show me vesting dates for May 2026"
- "What are the next 3 vesting dates?"
- "Get details for employees vesting on May 15"
- "Calculate taxes for this release"
- "Create a batch release"

---

## Folder Structure

```
vesting_agent/
├── agent.py                 # Defines the agent
├── tool.py                  # Functions the agent can call
├── utils.py                 # Helper functions
│
├── skills/                  # Workflows (how to handle requests)
│   ├── vesting_schedule/
│   │   └── SKILL.md        # How to show vesting info
│   └── release_workflow/
│       └── SKILL.md        # How to create releases
│
└── vesting_data/            # Data files
    ├── vesting_dates.csv   # Calendar of vesting dates
    └── vesting_details/    # Employee data for each date
        ├── 2026-05-15.csv
        ├── 2026-05-20.csv
        └── ...more dates
```

---

## Step 1: agent.py - Defining the Agent

**What it does**: Creates and configures the agent

```python
# File: vesting_agent/agent.py

from google.adk.agents.llm_agent import LlmAgent
from .tool import (
    get_vesting_dates,
    get_vesting_details,
    calculate_tax,
    filter_participants,
    # ... more tools
)
from app.agent.manager.utils import get_model

# Create the agent
vesting_agent = LlmAgent(
    name="VestingAgent",
    model="gemini-2.5-flash",      # Which AI model to use
    description="Handles vesting schedules and releases",
    instruction="""
        You are a vesting expert. Help users with:
        1. Vesting dates
        2. Participant details
        3. Tax calculations
        4. Release management
    """,
    tools=[
        get_vesting_dates,          # Tool 1: Get dates
        get_vesting_details,        # Tool 2: Get employee data
        calculate_tax,              # Tool 3: Calculate taxes
        filter_participants,        # Tool 4: Filter employees
    ]
)

# Root agent for web testing
root_agent = vesting_agent
```

### Key Points:
- **name**: What this agent is called
- **model**: Which AI to use (Google's Gemini)
- **instruction**: System prompt - tells AI what to do
- **tools**: Functions this agent can call

---

## Step 2: tool.py - The Functions

**What it does**: Defines all functions the agent can call

### Example Tool 1: Get Vesting Dates

```python
# File: vesting_agent/tool.py

def get_vesting_dates(
    client_id: str = "CLIENT_001",
    count: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict:
    """
    WHAT DOES IT DO?
    Returns vesting dates for a client with flexible filtering
    
    WHEN AGENT CALLS THIS:
    User: "Show me vesting dates for May 2026"
    Agent calls: get_vesting_dates(client_id="CLIENT_001", month=5, year=2026)
    
    HOW IT WORKS:
    1. Creates VestingDateService instance
    2. Loads vesting_dates.csv file
    3. Filters by parameters
    4. Returns result
    """
    try:
        service = VestingDateService()  # Load data
        
        # Determine what kind of filter to apply
        if count is not None:
            # User wants: "Next 3 dates"
            dates = service.get_next_n_dates(client_id, count)
            filter_type = f"next_{count}"
        elif month is not None:
            # User wants: "Dates in May 2026"
            dates = service.get_dates_in_month(client_id, month, year)
            filter_type = f"{month}/{year}"
        else:
            # User wants: "All dates"
            dates = service.get_all_dates(client_id)
            filter_type = "all"
        
        # Return formatted response
        return {
            "status": "success",
            "vesting_dates": dates,
            "client_id": client_id,
            "filter_type": filter_type,
            "total_found": len(dates),
            "message": f"Found {len(dates)} dates"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

### Key Points:
- **Parameters**: What the agent can pass in
- **Return value**: What the agent gets back
- **Error handling**: What if something goes wrong

### VestingDateService Class

This is the CORE helper class:

```python
class VestingDateService:
    """Manages vesting dates from CSV"""
    
    def __init__(self, csv_path=None):
        # Load vesting_dates.csv
        if csv_path is None:
            csv_path = Path(__file__).parent / "vesting_data" / "vesting_dates.csv"
        self.csv_path = csv_path
        self._df = None  # Cache (don't reload if not needed)
    
    def _load_csv(self) -> pd.DataFrame:
        """Load CSV file"""
        if self._df is None:
            # Lazy loading - only load when needed
            self._df = pd.read_csv(self.csv_path)
        return self._df
    
    def get_all_dates(self, client_id: str) -> List[str]:
        """Get all dates for client"""
        df = self._load_csv()
        dates = df[df["client_id"] == client_id]["vesting_date"].tolist()
        return sorted(dates)
    
    def get_next_n_dates(self, client_id: str, count: int) -> List[str]:
        """Get next N dates after today"""
        all_dates = self.get_all_dates(client_id)
        today = datetime.now().date()
        # Filter: only dates > today
        future_dates = [
            d for d in all_dates 
            if datetime.strptime(d, "%Y-%m-%d").date() > today
        ]
        return future_dates[:count]
    
    def get_dates_in_month(self, client_id: str, month: int, year: int) -> List[str]:
        """Get dates in a specific month"""
        all_dates = self.get_all_dates(client_id)
        month_dates = [
            d for d in all_dates
            if datetime.strptime(d, "%Y-%m-%d").month == month
            and datetime.strptime(d, "%Y-%m-%d").year == year
        ]
        return month_dates
```

### Key Points:
- **Lazy loading**: Only loads CSV when needed
- **Caching**: Stores result so it doesn't reload
- **Filtering**: Different methods for different queries

---

## Step 3: Data Files

### vesting_dates.csv

**Purpose**: Calendar of all vesting dates

```csv
client_id,vesting_date
CLIENT_001,2026-05-15
CLIENT_001,2026-05-20
CLIENT_001,2026-05-25
CLIENT_001,2026-06-15
CLIENT_001,2026-06-20
CLIENT_002,2026-04-10
CLIENT_002,2026-05-10
...
```

**What it contains**:
- Which clients exist
- When their employees' equity vests
- Very simple structure (only 2 columns!)

### vesting_details/*.csv

**Purpose**: Employee details for each vesting date

```csv
employee_id,employee_name,email,department,grant_type,shares_released,fmv_at_release,...
74069291,Taylor Randolph,ubutler@example.net,Finance,RSU,913,315656.71,...
31582740,Marcus Chen,mchen@example.com,Engineering,PSU,500,144830.77,...
58203617,Sophia Alvarez,salvarez@example.org,Sales,Stock Option,2000,625000.0,...
...
```

**What it contains**:
- Employee information
- Grant details
- Financial data
- Tax information

---

## Step 4: Skills - Define Workflows

### skills/vesting_schedule/SKILL.md

**Purpose**: Tells agent how to handle vesting schedule questions

```markdown
---
name: vesting-schedule
description: View vesting dates and participant details
---

# When User Asks:
- "Show me vesting dates"
- "What are the next 3 dates?"
- "Get details for May 15"

# Agent Should:
1. Call: get_vesting_dates()
2. Show results to user
3. Ask if they want details
4. If yes: Call get_vesting_details()
```

### skills/release_workflow/SKILL.md

**Purpose**: Tells agent how to create release batches

```markdown
---
name: release-workflow
description: Create and manage release batches
---

# When User Asks:
- "Create a release batch"
- "Process release for May 15"

# Agent Should:
1. Get vesting details
2. Filter participants
3. Calculate taxes
4. Create batch
5. Generate approval URL
```

### Key Points:
- Skills drive agent behavior
- They match user questions to tools
- They define the workflow order

---

## Complete Flow Example

### Scenario: User asks "Show me vesting dates for May 2026"

```
Step 1: USER SENDS MESSAGE
┌─────────────────────────────┐
│ "Show me vesting dates      │
│  for May 2026"              │
└─────────────────────────────┘
            ↓

Step 2: MANAGER AGENT ROUTES
┌─────────────────────────────┐
│ Manager analyzes message    │
│ Thinks: "This is vesting"   │
│ Routes to: vesting_agent    │
└─────────────────────────────┘
            ↓

Step 3: VESTING AGENT RECEIVES
┌─────────────────────────────┐
│ Receives: "Show vesting     │
│ dates for May 2026"         │
└─────────────────────────────┘
            ↓

Step 4: AGENT READS SKILLS
┌─────────────────────────────┐
│ Reads: vesting_schedule/    │
│        SKILL.md             │
│ Learns: Use                 │
│ get_vesting_dates()         │
└─────────────────────────────┘
            ↓

Step 5: AGENT CALLS TOOL
┌─────────────────────────────┐
│ Calls:                      │
│ get_vesting_dates(          │
│   client_id="CLIENT_001",   │
│   month=5,                  │
│   year=2026                 │
│ )                           │
└─────────────────────────────┘
            ↓

Step 6: TOOL LOADS DATA
┌─────────────────────────────┐
│ VestingDateService loads    │
│ vesting_dates.csv           │
│ Filters: month=5, year=2026 │
│ Result: [2026-05-15,        │
│          2026-05-20,        │
│          2026-05-25]        │
└─────────────────────────────┘
            ↓

Step 7: TOOL RETURNS RESULT
┌─────────────────────────────┐
│ {                           │
│   "status": "success",      │
│   "vesting_dates": [...],   │
│   "total_found": 3          │
│ }                           │
└─────────────────────────────┘
            ↓

Step 8: AGENT FORMATS RESPONSE
┌─────────────────────────────┐
│ "Found 3 vesting dates      │
│  in May 2026:               │
│  - May 15, 2026             │
│  - May 20, 2026             │
│  - May 25, 2026"            │
└─────────────────────────────┘
            ↓

Step 9: RESPONSE SENT TO USER
┌─────────────────────────────┐
│ Browser/App displays:       │
│ "Found 3 vesting dates      │
│  in May 2026:               │
│  - May 15, 2026             │
│  - May 20, 2026             │
│  - May 25, 2026"            │
└─────────────────────────────┘
```

---

## Code Patterns to Understand

### Pattern 1: Tool Function Structure

```python
def tool_function(param1: str, param2: int = None) -> Dict:
    """
    Docstring explains:
    - What it does
    - When agent calls it
    - What it returns
    """
    try:
        # Do the work
        result = process_data(param1, param2)
        
        # Return success
        return {
            "status": "success",
            "data": result,
            "message": "Operation completed"
        }
    except Exception as e:
        # Return error
        return {
            "status": "error",
            "message": str(e)
        }
```

### Pattern 2: Service Class

```python
class MyService:
    """Helper class that does real work"""
    
    def __init__(self):
        self._cache = None  # Caching pattern
    
    def _load_data(self):
        """Load data once"""
        if self._cache is None:
            self._cache = load_from_file()
        return self._cache
    
    def process_something(self, param):
        """Do actual work"""
        data = self._load_data()
        return filter_data(data, param)
```

### Pattern 3: Tool with Agent Integration

```python
def tool_for_agent(
    required_param: str,
    optional_param: Optional[str] = None,
    tool_context: ToolContext = None  # Session context
) -> Dict:
    """Tool that integrates with agent"""
    
    # Access session state if needed
    if tool_context:
        session_state = tool_context.state
    
    # Do work
    result = do_something()
    
    # Store result in session if needed
    if tool_context:
        tool_context.state["key"] = result
    
    return {
        "status": "success",
        "result": result
    }
```

---

## Learning Exercises

### Exercise 1: Trace a Request
1. Start at `/api/chat.py` - `chat_sse()` function
2. Follow to `/service/chat_service.py` - `exec_chat_sse()`
3. Follow to `/service/ai_workflow/runner_service.py` - `run_query_sse()`
4. Follow to manager agent in `/agent/manager/agent.py`
5. Follow to vesting_agent in `/agent/manager/sub_agent/vesting_agent/agent.py`
6. Look at `tool.py` to see what functions are available
7. Return back through the layers

### Exercise 2: Understand Tool Execution
1. Open `/agent/manager/sub_agent/vesting_agent/tool.py`
2. Find `get_vesting_dates()` function
3. Understand each parameter
4. Look at `VestingDateService` class
5. Trace how it loads CSV
6. See how it filters data
7. Follow what it returns

### Exercise 3: Add a New Tool
1. Add new function to `/agent/manager/sub_agent/vesting_agent/tool.py`
2. Register it in `/agent/manager/sub_agent/vesting_agent/agent.py`
3. Test by asking the agent to use it

### Exercise 4: Understand Skills
1. Open `/agent/manager/sub_agent/vesting_agent/skills/vesting_schedule/SKILL.md`
2. Read what it says about workflows
3. Open `/agent/manager/sub_agent/vesting_agent/skills/release_workflow/SKILL.md`
4. Compare the two workflows

---

## Common Questions Answered

**Q: How does agent know when to call which tool?**
- A: It reads the skills (SKILL.md) which tell it which tools to use for different questions

**Q: How does agent get context from previous messages?**
- A: Runner loads session history from database, passes to agent

**Q: Can I add new tools?**
- A: Yes! Add function to tool.py, register in agent.py

**Q: How is data stored?**
- A: CSV files for vesting data, SQLite database for chat history

**Q: What if tool fails?**
- A: It returns error status, agent can retry or tell user

**Q: Can multiple agents work together?**
- A: Yes! Manager routes to appropriate agent

---

## Next Steps for Learning

1. **Run the system**: Send a message and trace through layers
2. **Add a tool**: Create new function in tool.py
3. **Modify a skill**: Change SKILL.md to handle new use case
4. **Debug**: Use print statements to see what's happening
5. **Read Google ADK docs**: Understand LlmAgent better

Happy learning! 🚀
