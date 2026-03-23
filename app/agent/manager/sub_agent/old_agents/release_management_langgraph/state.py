"""
State schema for the Release Management Agent using LangGraph.
"""

from typing import TypedDict, List, Tuple, Optional, Annotated
from operator import add


class AgentState(TypedDict):
    """
    State schema for the release management workflow.

    Attributes:
        messages: Conversation history (accumulated)
        token_vesting_list: List of (vesting_date, token_id) tuples
        current_vesting_date: Currently selected vesting date
        fmv: Fair Market Value per unit
        sales_price: Sales price per unit
        workflow_stage: Current stage in the workflow
        user_intent: Classified user intent
    """
    messages: Annotated[List[dict], add]  # Accumulate messages
    token_vesting_list: List[Tuple[str, str]]  # [(vesting_date, token_id)]
    current_vesting_date: Optional[str]
    fmv: Optional[float]
    sales_price: Optional[float]
    workflow_stage: str  # "welcome", "vesting_dates", "vesting_details", "collect_inputs", "calculate_tax", "complete"
    user_intent: Optional[str]  # "tax_calculation", "release_management", "data_analysis", etc.
