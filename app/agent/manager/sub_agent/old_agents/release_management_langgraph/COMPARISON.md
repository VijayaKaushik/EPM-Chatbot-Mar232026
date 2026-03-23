# Google ADK vs LangGraph Implementation Comparison

## Side-by-Side Code Comparison

### 1. Agent Definition

**Google ADK**
```python
from google.adk.agents import LlmAgent
from google.adk.tools import skill_toolset

root_agent = LlmAgent(
    name="releasemanagement_agent",
    model="gemini-2.5-flash",
    instruction="...",
    tools=[calculate_tax, get_vesting_dates, get_vesting_details, my_skill_toolset],
)
```

**LangGraph**
```python
from langgraph.graph import StateGraph
from .state import AgentState
from .nodes import welcome_node, get_dates_node, ...

workflow = StateGraph(AgentState)
workflow.add_node("welcome", welcome_node)
workflow.add_node("get_dates", get_dates_node)
# ... add more nodes
workflow.set_entry_point("welcome")
# ... add edges
graph = workflow.compile()
```

### 2. State Management

**Google ADK**
```python
def get_vesting_details(vesting_date: str, tool_context: ToolContext) -> Dict:
    token_id = f"token_{uuid.uuid4().hex[:8]}"

    # Access state
    tool_vesting_list = tool_context.state.get("token_vesting_list")
    if tool_vesting_list is None:
        tool_vesting_list = []

    tool_vesting_list.append((vesting_date, token_id))

    # Update state
    tool_context.state["token_vesting_list"] = tool_vesting_list

    return {"status": "success", ...}
```

**LangGraph**
```python
class AgentState(TypedDict):
    messages: Annotated[List[dict], add]
    token_vesting_list: List[Tuple[str, str]]
    current_vesting_date: Optional[str]
    # ... more fields

def get_details_node(state: AgentState) -> Dict[str, Any]:
    vesting_date = state.get("current_vesting_date")
    result = get_vesting_details(vesting_date)
    token_id = result.get("token_id")

    # Update state
    token_list = state.get("token_vesting_list", [])
    token_list.append((vesting_date, token_id))

    return {
        "token_vesting_list": token_list,
        "current_vesting_date": vesting_date,
        "workflow_stage": "collect_inputs",
    }
```

### 3. Skills vs Nodes

**Google ADK Skills**
```markdown
# SKILL.md
---
name: vesting-tax-calculation
description: Calculate vesting taxes...
---

## Stage 1: Get Vesting Dates
**Tool**: `get_vesting_dates(count: int = 1)`
1. Parse count from user message
2. Call tool and display dates
3. Ask which date(s) to process
```

**LangGraph Nodes**
```python
def get_dates_node(state: AgentState) -> Dict[str, Any]:
    count = 3  # Default
    result = get_vesting_dates(count)
    dates = result.get("vesting_dates", [])

    dates_list = "\n".join([f"{i+1}. {date}" for i, date in enumerate(dates)])
    response = f"Available vesting dates:\n{dates_list}\n\nWhich date?"

    return {
        "messages": [{"role": "assistant", "content": response}],
        "workflow_stage": "vesting_details",
    }
```

### 4. Tool Definitions

**Google ADK**
```python
from google.adk.tools.tool_context import ToolContext

def calculate_tax(
    vesting_date: str,
    fmv: float,
    sales: float,
    tool_context: ToolContext
) -> Dict:
    # Access state through context
    tool_vesting_list = tool_context.state["token_vesting_list"]

    # Find token
    token_id = None
    for tool_vesting_date in tool_vesting_list:
        if tool_vesting_date[0] == vesting_date:
            token_id = tool_vesting_date[1]

    return {"status": "success", ...}
```

**LangGraph**
```python
# Pure function - no context needed
def calculate_tax(vesting_date: str, fmv: float, sales: float, token_id: str) -> Dict:
    # Direct parameters - state managed at node level
    estimated_tax = 200000

    return {
        "status": "success",
        "summary": f"Tax: ${estimated_tax}",
        "approval_url": f"https://approval.example.com/{token_id}",
    }

# Node handles state lookup
def calculate_tax_node(state: AgentState) -> Dict[str, Any]:
    vesting_date = state.get("current_vesting_date")
    fmv = state.get("fmv")
    sales = state.get("sales_price")

    # Find token from state
    token_list = state.get("token_vesting_list", [])
    token_id = next((tid for date, tid in token_list if date == vesting_date), None)

    # Call pure tool
    result = calculate_tax(vesting_date, fmv, sales, token_id)

    return {
        "messages": [{"role": "assistant", "content": result["summary"]}],
        "workflow_stage": "complete",
    }
```

### 5. Workflow Routing

**Google ADK**
```python
# Implicit routing through skill definitions and LLM decisions
instruction = """
SKILLS AVAILABLE:
- welcome-intent: Greet users and understand their intent
- googleadk-vesting-tax: Execute vesting tax calculation workflows

APPROACH:
- Use welcome-intent skill for new users or unclear requests
- Use googleadk-vesting-tax skill for tax calculation workflows
"""
```

**LangGraph**
```python
# Explicit routing through conditional edges
workflow.add_conditional_edges(
    "welcome",
    lambda state: state.get("workflow_stage", "welcome"),
    {
        "welcome": END,
        "vesting_dates": "get_dates",
    }
)

workflow.add_conditional_edges(
    "get_dates",
    lambda state: state.get("workflow_stage", "complete"),
    {
        "vesting_details": "get_details",
        "complete": END,
    }
)
```

### 6. Execution

**Google ADK**
```python
# Agent handles everything internally
response = root_agent.run("Calculate vesting taxes")
```

**LangGraph**
```python
# Explicit state management
state = {
    "messages": [{"role": "user", "content": "Calculate vesting taxes"}],
    "token_vesting_list": [],
    "workflow_stage": "welcome",
}

result = graph.invoke(state)
response = result["messages"][-1]["content"]
```

## Architecture Comparison

### Google ADK Architecture

```
┌─────────────────────────────────────────┐
│          LlmAgent (Gemini)              │
│  ┌─────────────────────────────────┐   │
│  │      Skill Toolset              │   │
│  │  ┌──────────────────────────┐   │   │
│  │  │  tax_calculation_skill   │   │   │
│  │  │  welcome_intent_skill    │   │   │
│  │  └──────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │         Direct Tools            │   │
│  │  - get_vesting_dates            │   │
│  │  - get_vesting_details          │   │
│  │  - calculate_tax                │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
         ▼
   ToolContext.state
```

### LangGraph Architecture

```
┌─────────────────────────────────────────┐
│         StateGraph                      │
│  ┌─────────────────────────────────┐   │
│  │           Nodes                 │   │
│  │  ┌──────────────────────────┐   │   │
│  │  │  welcome_node            │   │   │
│  │  │  get_dates_node          │   │   │
│  │  │  get_details_node        │   │   │
│  │  │  collect_inputs_node     │   │   │
│  │  │  calculate_tax_node      │   │   │
│  │  └──────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    Conditional Edges            │   │
│  │  (workflow_stage routing)       │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
         ▼
    AgentState (TypedDict)
         │
         ▼
   Tools (pure functions)
```

## Key Differences Summary

| Feature | Google ADK | LangGraph |
|---------|-----------|-----------|
| **State Type** | `dict` via `ToolContext` | `TypedDict` with schema |
| **Workflow Definition** | Skill markdown + LLM interpretation | Explicit graph with nodes/edges |
| **Tool Context** | Passed as `tool_context` parameter | State passed to nodes, not tools |
| **Routing Logic** | LLM-driven skill selection | Conditional edges based on state |
| **Type Safety** | Runtime checks | Compile-time via TypedDict |
| **Debuggability** | Black box LLM decisions | Inspectable graph structure |
| **Testing** | Integration testing primarily | Unit test nodes/tools separately |
| **Visualization** | N/A | Graph visualization available |
| **Vendor Lock-in** | Google ADK proprietary | Open-source LangGraph |
| **LLM Usage** | Every decision point | Can be selective (nodes only) |
| **State Mutations** | Direct mutation in tools | Immutable returns from nodes |
| **Error Handling** | Skill-level guidance | Node-level explicit handling |

## When to Use Each

### Use Google ADK When:
- You want LLM to handle routing and decisions
- You prefer markdown-driven skill definitions
- You're fully invested in Google's ecosystem
- You want natural language workflow orchestration

### Use LangGraph When:
- You need explicit control over workflow logic
- You want type-safe state management
- You need to unit test individual components
- You want to visualize and debug the workflow
- You prefer open-source solutions
- You need fine-grained control over LLM usage

## Migration Path

To migrate from Google ADK to LangGraph:

1. **Extract State Schema**: Define `TypedDict` from `ToolContext.state` usage
2. **Convert Skills to Nodes**: Each skill stage becomes a node function
3. **Remove Tool Context**: Make tools pure functions, handle state in nodes
4. **Define Graph**: Map skill transitions to edges
5. **Add Conditionals**: Replace LLM-driven routing with conditional logic
6. **Test Nodes**: Unit test each node independently
7. **Integrate**: Connect to your application

## Conclusion

Both implementations achieve the same goal with different philosophies:

- **Google ADK**: LLM-centric, declarative, vendor-specific
- **LangGraph**: Code-centric, explicit, open-source

Choose based on your needs for control, testability, and ecosystem preferences.
