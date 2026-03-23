"""
Example usage of the Release Management LangGraph agent.
"""

from graph import create_release_management_graph, run_workflow


def main():
    """Run example conversation."""
    print("=" * 60)
    print("Release Management Agent - LangGraph Example")
    print("=" * 60)

    # Create the graph
    graph = create_release_management_graph()

    # Example 1: Full workflow
    print("\n--- Example 1: Full Tax Calculation Workflow ---\n")

    state = None

    # Step 1: Greet and state intent
    print("User: I need to calculate vesting taxes")
    state = run_workflow(graph, "I need to calculate vesting taxes", state)
    print(f"Assistant: {state['messages'][-1]['content']}\n")

    # Step 2: Select date
    print("User: 2026-03-15")
    state = run_workflow(graph, "2026-03-15", state)
    print(f"Assistant: {state['messages'][-1]['content']}\n")

    # Step 3: Provide FMV and sales price
    print("User: FMV is $100, sales price is $120")
    state = run_workflow(graph, "FMV is $100, sales price is $120", state)
    print(f"Assistant: {state['messages'][-1]['content']}\n")

    # Example 2: Unclear intent
    print("\n--- Example 2: Unclear Intent ---\n")

    state = None

    print("User: Hello")
    state = run_workflow(graph, "Hello", state)
    print(f"Assistant: {state['messages'][-1]['content']}\n")

    # Example 3: Direct access to nodes
    print("\n--- Example 3: Testing Individual Nodes ---\n")

    from nodes import welcome_node, get_dates_node

    # Test welcome node
    test_state = {
        "messages": [{"role": "user", "content": "Calculate taxes"}],
        "workflow_stage": "welcome",
        "token_vesting_list": [],
    }
    result = welcome_node(test_state)
    print(f"Welcome Node - Intent: {result.get('user_intent')}")
    print(f"Welcome Node - Next Stage: {result.get('workflow_stage')}\n")

    # Test get_dates node
    test_state = {"workflow_stage": "vesting_dates"}
    result = get_dates_node(test_state)
    print(f"Get Dates Node - Response: {result['messages'][-1]['content'][:100]}...\n")

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
