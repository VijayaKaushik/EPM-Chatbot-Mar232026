"""
Main LangGraph workflow for Release Management Agent.
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    welcome_node,
    get_dates_node,
    get_details_node,
    collect_inputs_node,
    calculate_tax_node,
    router_node,
)


def create_release_management_graph():
    """
    Creates and returns the release management workflow graph.

    Returns:
        Compiled LangGraph StateGraph
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("welcome", welcome_node)
    workflow.add_node("get_dates", get_dates_node)
    workflow.add_node("get_details", get_details_node)
    workflow.add_node("collect_inputs", collect_inputs_node)
    workflow.add_node("calculate_tax", calculate_tax_node)

    # Set entry point
    workflow.set_entry_point("welcome")

    # Add conditional edges based on workflow_stage
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

    workflow.add_conditional_edges(
        "get_details",
        lambda state: state.get("workflow_stage", "collect_inputs"),
        {
            "collect_inputs": "collect_inputs",
            "vesting_details": "get_details",
        }
    )

    workflow.add_conditional_edges(
        "collect_inputs",
        lambda state: state.get("workflow_stage", "collect_inputs"),
        {
            "collect_inputs": END,
            "calculate_tax": "calculate_tax",
        }
    )

    workflow.add_edge("calculate_tax", END)

    # Compile the graph
    return workflow.compile()


def run_workflow(graph, user_input: str, state: dict = None):
    """
    Run the workflow with a user input.

    Args:
        graph: Compiled LangGraph
        user_input: User's message
        state: Existing state (optional)

    Returns:
        Updated state after processing
    """
    if state is None:
        state = {
            "messages": [],
            "token_vesting_list": [],
            "current_vesting_date": None,
            "fmv": None,
            "sales_price": None,
            "workflow_stage": "welcome",
            "user_intent": None,
        }

    # Add user message to state
    state["messages"].append({"role": "user", "content": user_input})

    # Run the graph
    result = graph.invoke(state)

    return result
