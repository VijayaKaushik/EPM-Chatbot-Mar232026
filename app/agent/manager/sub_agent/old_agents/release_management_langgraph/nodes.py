"""
Workflow nodes for the Release Management LangGraph agent.
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from .state import AgentState
from .tools import get_vesting_dates, get_vesting_details, calculate_tax


def welcome_node(state: AgentState) -> Dict[str, Any]:
    """
    Greet user and understand their intent.
    """
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    # Check if user has clear intent
    if last_message:
        user_msg = last_message.get("content", "").lower()

        # Classify intent
        if any(keyword in user_msg for keyword in ["tax", "calculate", "vesting"]):
            intent = "tax_calculation"
            next_stage = "vesting_dates"
            response = "I'll help you calculate vesting taxes. Let me retrieve available vesting dates..."
        else:
            intent = None
            next_stage = "welcome"
            response = (
                "Hello! Welcome to the Release Management Assistant.\n\n"
                "I can help you with:\n"
                "• Vesting tax calculations\n"
                "• Release schedule tracking\n"
                "• Data analysis and reports\n\n"
                "What would you like to do today?"
            )
    else:
        intent = None
        next_stage = "welcome"
        response = "Hello! How can I assist you today?"

    return {
        "messages": [{"role": "assistant", "content": response}],
        "user_intent": intent,
        "workflow_stage": next_stage,
    }


def get_dates_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieve and present vesting dates.
    """
    # Default to 3 dates
    count = 3

    result = get_vesting_dates(count)
    dates = result.get("vesting_dates", [])

    if dates:
        dates_list = "\n".join([f"{i+1}. {date}" for i, date in enumerate(dates)])
        response = (
            f"Available vesting dates:\n{dates_list}\n\n"
            "Which date would you like to process? (Please specify the date or number)"
        )
        next_stage = "vesting_details"
    else:
        response = "No upcoming vesting dates found. Please check the vesting schedule."
        next_stage = "complete"

    return {
        "messages": [{"role": "assistant", "content": response}],
        "workflow_stage": next_stage,
    }


def get_details_node(state: AgentState) -> Dict[str, Any]:
    """
    Get vesting details and create token.
    """
    vesting_date = state.get("current_vesting_date")

    if not vesting_date:
        # Try to extract from last message
        messages = state.get("messages", [])
        if messages:
            last_msg = messages[-1].get("content", "")
            # Simple extraction - in production, use better parsing
            for word in last_msg.split():
                if len(word) == 10 and word.count("-") == 2:
                    vesting_date = word
                    break

    if not vesting_date:
        return {
            "messages": [{"role": "assistant", "content": "Please specify a valid vesting date (YYYY-MM-DD)."}],
            "workflow_stage": "vesting_details",
        }

    result = get_vesting_details(vesting_date)
    token_id = result.get("token_id")
    participant_count = result.get("participant_count", 0)
    total_units = result.get("total_units", 0)

    # Update token list
    token_list = state.get("token_vesting_list", [])
    token_list.append((vesting_date, token_id))

    response = (
        f"✓ Token created for {vesting_date}\n\n"
        f"Participant Summary:\n"
        f"• Total participants: {participant_count}\n"
        f"• Total units vesting: {total_units:,}\n\n"
        "Please provide:\n"
        "• FMV (Fair Market Value per unit): $___\n"
        "• Sales Price (per unit): $___"
    )

    return {
        "messages": [{"role": "assistant", "content": response}],
        "token_vesting_list": token_list,
        "current_vesting_date": vesting_date,
        "workflow_stage": "collect_inputs",
    }


def collect_inputs_node(state: AgentState) -> Dict[str, Any]:
    """
    Collect FMV and sales price from user.
    """
    messages = state.get("messages", [])
    last_msg = messages[-1].get("content", "") if messages else ""

    # Simple parsing - in production, use better extraction
    fmv = state.get("fmv")
    sales = state.get("sales_price")

    # Try to extract numbers from message
    import re
    numbers = re.findall(r'\d+\.?\d*', last_msg)

    if len(numbers) >= 2 and not fmv and not sales:
        fmv = float(numbers[0])
        sales = float(numbers[1])
    elif fmv and sales:
        # Already have values, confirm
        vesting_date = state.get("current_vesting_date")
        response = (
            f"Confirmed values for {vesting_date}:\n"
            f"• FMV: ${fmv:.2f}\n"
            f"• Sales Price: ${sales:.2f}\n\n"
            "Calculating taxes..."
        )
        return {
            "messages": [{"role": "assistant", "content": response}],
            "fmv": fmv,
            "sales_price": sales,
            "workflow_stage": "calculate_tax",
        }
    else:
        response = (
            "Please provide both values:\n"
            "• FMV (Fair Market Value): $___\n"
            "• Sales Price: $___\n\n"
            "Example: FMV is $100, sales price is $120"
        )
        return {
            "messages": [{"role": "assistant", "content": response}],
            "workflow_stage": "collect_inputs",
        }

    return {
        "messages": [{"role": "assistant", "content": "Values received. Proceeding to calculate taxes..."}],
        "fmv": fmv,
        "sales_price": sales,
        "workflow_stage": "calculate_tax",
    }


def calculate_tax_node(state: AgentState) -> Dict[str, Any]:
    """
    Calculate tax and present results.
    """
    vesting_date = state.get("current_vesting_date")
    fmv = state.get("fmv")
    sales = state.get("sales_price")
    token_list = state.get("token_vesting_list", [])

    # Find token for this vesting date
    token_id = None
    for date, tid in token_list:
        if date == vesting_date:
            token_id = tid
            break

    if not token_id:
        return {
            "messages": [{"role": "assistant", "content": "Error: Token not found. Please start over."}],
            "workflow_stage": "complete",
        }

    if not fmv or not sales:
        return {
            "messages": [{"role": "assistant", "content": "Error: FMV and sales price required."}],
            "workflow_stage": "collect_inputs",
        }

    result = calculate_tax(vesting_date, fmv, sales, token_id)
    summary = result.get("summary", "")
    approval_url = result.get("approval_url", "")

    response = (
        f"{summary}\n\n"
        f"📋 Review and approve: {approval_url}\n\n"
        "Tax calculation complete! Would you like to process another date?"
    )

    return {
        "messages": [{"role": "assistant", "content": response}],
        "workflow_stage": "complete",
    }


def router_node(state: AgentState) -> str:
    """
    Route to next node based on workflow stage.
    """
    stage = state.get("workflow_stage", "welcome")

    stage_map = {
        "welcome": "welcome",
        "vesting_dates": "get_dates",
        "vesting_details": "get_details",
        "collect_inputs": "collect_inputs",
        "calculate_tax": "calculate_tax",
        "complete": "END",
    }

    return stage_map.get(stage, "END")
