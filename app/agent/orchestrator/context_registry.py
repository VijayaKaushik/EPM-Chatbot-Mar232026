from typing import Dict, List, Optional

from google.adk.tools.tool_context import ToolContext


class ContextRegistry:
    """
    Reads and writes lightweight turn summaries to ADK session state.
    Never stores full records — only keys and scalars.
    """

    def write_turn(
        self,
        tool_context: ToolContext,
        turn_index: int,
        agent_name: str,
        intent: str,
        employee_ids: Optional[List[str]] = None,
        vesting_date: Optional[str] = None,
        batch_id: Optional[str] = None,
        summary: Optional[Dict] = None,
    ) -> None:
        """Write lightweight turn summary to session state."""
        registry = tool_context.state.get("context_registry", {})
        registry[f"turn_{turn_index}"] = {
            "agent":        agent_name,
            "intent":       intent,
            "employee_ids": employee_ids or [],
            "vesting_date": vesting_date,
            "batch_id":     batch_id,
            "summary":      summary or {},
        }
        tool_context.state["context_registry"] = registry
        tool_context.state["turn_index"] = turn_index + 1

    def read_registry(self, tool_context: ToolContext) -> Dict:
        """Read full context registry from session state."""
        return tool_context.state.get("context_registry", {})

    def get_latest_employee_ids(self, tool_context: ToolContext) -> List[str]:
        """Get employee_ids from most recent turn that has them."""
        registry = self.read_registry(tool_context)
        for turn in reversed(list(registry.values())):
            if turn.get("employee_ids"):
                return turn["employee_ids"]
        return []

    def get_latest_vesting_date(self, tool_context: ToolContext) -> Optional[str]:
        """Get most recent vesting_date from registry."""
        registry = self.read_registry(tool_context)
        for turn in reversed(list(registry.values())):
            if turn.get("vesting_date"):
                return turn["vesting_date"]
        return None

    def get_turn_index(self, tool_context: ToolContext) -> int:
        return tool_context.state.get("turn_index", 0)
