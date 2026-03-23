"""
Release Management Agent with Planning, Filtering, and Batch Creation.

Provides enhanced workflow orchestration with:
- Execution planning before tool calls
- Smart filtering of tranche data
- Batch creation with approval workflows
"""

from .agent import root_agent

__all__ = ["root_agent"]
