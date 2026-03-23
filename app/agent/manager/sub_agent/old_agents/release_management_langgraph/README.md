# Release Management Agent - LangGraph Implementation

A conversational agent for vesting tax calculations and release management, built with LangGraph for workflow orchestration.

## Overview

This package is a LangGraph-based conversion of the Google ADK `releasemanagement_agent`. It provides the same functionality using LangGraph's state management and workflow graph capabilities.

## Architecture

### Core Components

**State Management** (`state.py`)
- `AgentState`: TypedDict schema defining workflow state
- Tracks conversation, tokens, inputs, and workflow stage

**Tools** (`tools.py`)
- `get_vesting_dates()`: Retrieve available vesting dates
- `get_vesting_details()`: Create token and get participant info
- `calculate_tax()`: Calculate tax and generate approval URL

**Nodes** (`nodes.py`)
- `welcome_node`: Greet and classify user intent
- `get_dates_node`: Present vesting dates
- `get_details_node`: Create token and show details
- `collect_inputs_node`: Get FMV and sales price
- `calculate_tax_node`: Calculate and present results

**Graph** (`graph.py`)
- `create_release_management_graph()`: Build workflow graph
- `run_workflow()`: Execute graph with user input

### Workflow Graph

```
START
  ↓
welcome_node
  ↓
[intent == "tax_calculation"]
  ↓
get_dates_node
  ↓
get_details_node
  ↓
collect_inputs_node
  ↓
calculate_tax_node
  ↓
END
```

## Usage

### Basic Usage

```python
from app.agent.manager.sub_agent.old_agents.release_management_langgraph import (
    create_release_management_graph
)

# Create the graph
graph = create_release_management_graph()

# Initialize state
state = {
    "messages": [],
    "token_vesting_list": [],
    "current_vesting_date": None,
    "fmv": None,
    "sales_price": None,
    "workflow_stage": "welcome",
    "user_intent": None,
}

# Run with user input
state["messages"].append({"role": "user", "content": "I need to calculate vesting taxes"})
result = graph.invoke(state)

# Get assistant response
last_message = result["messages"][-1]
print(last_message["content"])
```

### Multi-Turn Conversation

```python
# First turn: Greet
state["messages"].append({"role": "user", "content": "Hello"})
result = graph.invoke(state)
state = result

# Second turn: Request tax calculation
state["messages"].append({"role": "user", "content": "Calculate taxes for next vesting"})
result = graph.invoke(state)
state = result

# Third turn: Select date
state["messages"].append({"role": "user", "content": "2026-03-15"})
result = graph.invoke(state)
state = result

# Fourth turn: Provide FMV and sales
state["messages"].append({"role": "user", "content": "FMV is $100, sales is $120"})
result = graph.invoke(state)
state = result
```

### Using run_workflow Helper

```python
from app.agent.manager.sub_agent.old_agents.release_management_langgraph import (
    run_workflow,
    create_release_management_graph
)

graph = create_release_management_graph()

# First message
result = run_workflow(graph, "Calculate vesting taxes")
print(result["messages"][-1]["content"])

# Continue conversation
result = run_workflow(graph, "2026-03-15", state=result)
print(result["messages"][-1]["content"])

result = run_workflow(graph, "FMV is $100, sales is $120", state=result)
print(result["messages"][-1]["content"])
```

## State Schema

```python
class AgentState(TypedDict):
    messages: List[dict]  # Conversation history
    token_vesting_list: List[Tuple[str, str]]  # [(date, token_id)]
    current_vesting_date: Optional[str]  # Selected date
    fmv: Optional[float]  # Fair Market Value
    sales_price: Optional[float]  # Sales price per unit
    workflow_stage: str  # Current stage
    user_intent: Optional[str]  # Classified intent
```

## Differences from Google ADK Version

| Aspect | Google ADK | LangGraph |
|--------|-----------|-----------|
| State Management | `ToolContext.state` | `AgentState` TypedDict |
| Workflow | Skill-based | Graph nodes with edges |
| Tools | ADK tools with context | Pure Python functions |
| Skills | SKILL.md driven | Node-based implementation |
| Routing | Skill orchestration | Conditional edges |
| State Passing | `tool_context` parameter | State dict returned by nodes |

## Advantages of LangGraph Version

1. **Explicit State Schema**: TypedDict provides type safety
2. **Visual Workflow**: Graph structure is clear and inspectable
3. **Testability**: Each node is a pure function
4. **Debugging**: State transitions are explicit
5. **Flexibility**: Easy to add branches and conditions
6. **No Vendor Lock-in**: Open-source LangGraph vs proprietary ADK

## Testing

```python
from app.agent.manager.sub_agent.old_agents.release_management_langgraph import (
    welcome_node,
    get_dates_node
)

# Test welcome node
state = {
    "messages": [{"role": "user", "content": "Calculate taxes"}],
    "workflow_stage": "welcome",
}
result = welcome_node(state)
assert result["user_intent"] == "tax_calculation"
assert result["workflow_stage"] == "vesting_dates"

# Test get_dates node
state = {"workflow_stage": "vesting_dates"}
result = get_dates_node(state)
assert "2026-03-15" in result["messages"][-1]["content"]
```

## Extension Points

### Adding New Nodes

```python
def new_node(state: AgentState) -> Dict[str, Any]:
    # Node logic here
    return {
        "messages": [{"role": "assistant", "content": "response"}],
        "workflow_stage": "next_stage",
    }

# Add to graph
workflow.add_node("new_node", new_node)
workflow.add_edge("previous_node", "new_node")
```

### Adding New Tools

```python
# In tools.py
def new_tool(param: str) -> Dict:
    # Tool logic
    return {"status": "success", "data": "..."}

# Use in node
def node_using_tool(state: AgentState) -> Dict[str, Any]:
    result = new_tool(state.get("param"))
    return {"messages": [...]}
```

## Requirements

```
langgraph>=0.0.40
langchain-core>=0.1.0
```

## License

Same as parent project.
