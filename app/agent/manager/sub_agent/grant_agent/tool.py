import json
import os
import pathlib
from typing import Dict, List, Optional

import pandas as pd
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types
from pandasai.llm.base import LLM as _PaiLLM

GRANT_DATA_PATH = pathlib.Path(__file__).parent / "grant_data" / "grants.json"
ARTIFACT_KEY    = "grants_data.json"


class GeminiLLM(_PaiLLM):
    """PandasAI-compatible LLM wrapper using Google Gemini via google-genai."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__(api_key=api_key)
        from google import genai

        self.model = model
        self._client = genai.Client(api_key=api_key)

    @property
    def type(self) -> str:
        return "google-gemini"

    def call(self, instruction, context=None) -> str:
        prompt = instruction.to_string() if hasattr(instruction, "to_string") else str(instruction)
        self.last_prompt = prompt
        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text


async def _load_artifact(tool_context: ToolContext) -> Optional[Dict]:
    """Try to load grants from artifact. Returns None if not found."""
    try:
        artifact = await tool_context.load_artifact(ARTIFACT_KEY)
        if artifact and artifact.text:
            return json.loads(artifact.text)
    except Exception:
        pass
    return None


async def _save_artifact(tool_context: ToolContext, data: Dict,
                         key: str = ARTIFACT_KEY) -> None:
    """Save data dict to ADK artifact."""
    await tool_context.save_artifact(
        filename=key,
        artifact=genai_types.Part(text=json.dumps(data))
    )


def _compute_summary(data: Dict) -> Dict:
    """Compute summary counts from grant data."""
    grants = data["grants"]
    by_type   = {}
    by_plan   = {}
    by_status = {}
    for g in grants:
        by_type[g["grant_type"]]     = by_type.get(g["grant_type"], 0) + 1
        by_plan[g["plan_id"]]        = by_plan.get(g["plan_id"], 0) + 1
        by_status[g["grant_status"]] = by_status.get(g["grant_status"], 0) + 1
    return {
        "total_grants":    len(grants),
        "total_employees": len({g["employee_id"] for g in grants}),
        "by_grant_type":   by_type,
        "by_plan":         by_plan,
        "by_status":       by_status,
    }


async def load_grants(tool_context: ToolContext) -> Dict:
    """
    Loads grant data into ADK artifact for session persistence.
    First call reads from disk and saves to artifact.
    Subsequent calls return summary from existing artifact — no disk I/O.

    LLM Prompt Examples:
      - 'Load grant data'
      - 'Initialize grants'
      - Called automatically before any other grant tool

    Returns:
      status, source (disk|artifact), total_grants, total_employees,
      by_grant_type, by_plan, by_status, message
    """
    # Check if artifact already exists
    existing = await _load_artifact(tool_context)
    if existing:
        summary = _compute_summary(existing)
        return {
            "status":  "success",
            "source":  "artifact",
            **summary,
            "message": "Grant data already loaded from artifact"
        }

    # Load from disk
    if not GRANT_DATA_PATH.exists():
        return {
            "status":  "error",
            "message": f"Grant data file not found: {GRANT_DATA_PATH}"
        }

    data = json.loads(GRANT_DATA_PATH.read_text())

    # Save to artifact
    await _save_artifact(tool_context, data, ARTIFACT_KEY)

    summary = _compute_summary(data)
    return {
        "status":  "success",
        "source":  "disk",
        **summary,
        "message": f"Loaded {summary['total_grants']} grants and saved to artifact"
    }


async def query_grants(query: str, tool_context: ToolContext) -> Dict:
    """
    Analyzes grant data using natural language via PandasAI.
    Reads from artifact — no disk I/O after first load.
    Saves query result to artifact for reuse.

    Args:
        query: Natural language question about grants

    LLM Prompt Examples:
      - 'Which grant type has maximum unvested shares?'
      - 'Show grants by officer status'
      - 'How many active RSU grants are there?'
      - 'Which plan has the most grants?'
      - 'Show average grant value by grant type'
      - 'List grants expiring in next 90 days'
      - 'Which employees have more than 2 grants?'
      - 'Show cancelled grants by employee'
      - 'Breakdown of grants by status'
      - 'Which grant type has highest percentage vested?'

    Returns:
      status, source, query, result, total_rows, message
    """
    try:
        from pandasai.agent import Agent as PaiAgent

        # Load from artifact or disk
        data = await _load_artifact(tool_context)
        if not data:
            load_result = await load_grants(tool_context)
            if load_result["status"] != "success":
                return {
                    "status":  "error",
                    "query":   query,
                    "result":  None,
                    "message": "Failed to load grant data"
                }
            data = await _load_artifact(tool_context)

        # Flatten grants list to DataFrame
        df = pd.DataFrame(data["grants"])

        api_key = os.environ.get("GOOGLE_API_KEY", "")
        llm     = GeminiLLM(api_key=api_key, model="gemini-2.5-flash")
        agent   = PaiAgent(df, config={"llm": llm})
        result  = agent.chat(query)

        if isinstance(result, pd.DataFrame):
            result_str = result.to_markdown(index=False)
        elif isinstance(result, pd.Series):
            result_str = result.to_markdown()
        else:
            result_str = str(result)

        # Save query result to artifact
        await _save_artifact(
            tool_context,
            {"query": query, "result": result_str},
            "grant_query_result.json"
        )

        return {
            "status":     "success",
            "source":     "artifact",
            "query":      query,
            "result":     result_str,
            "total_rows": len(df),
            "message":    "Analysis completed successfully"
        }

    except Exception as e:
        return {
            "status":  "error",
            "query":   query,
            "result":  None,
            "message": f"Analysis failed: {str(e)}"
        }


async def get_grant_details(
    grant_id: str,
    tool_context: ToolContext
) -> Dict:
    """
    Returns full details for a specific grant by grant_id.
    Reads from artifact — no disk I/O after first load.
    Saves individual grant to its own artifact.

    Args:
        grant_id: The grant ID to look up (e.g. GR-8FE49167-861)

    LLM Prompt Examples:
      - 'Show details for grant GR-8FE49167-861'
      - 'Get full information for this grant'
      - 'What are the conditions for this grant?'

    Returns:
      status, grant_id, grant (full record), message
    """
    data = await _load_artifact(tool_context)
    if not data:
        await load_grants(tool_context)
        data = await _load_artifact(tool_context)

    match = next(
        (g for g in data["grants"] if g["grant_id"] == grant_id),
        None
    )

    if not match:
        return {
            "status":   "not_found",
            "grant_id": grant_id,
            "message":  f"No grant found with ID {grant_id}"
        }

    # Save to its own artifact
    artifact_key = f"grant_detail_{grant_id}.json"
    await _save_artifact(tool_context, match, artifact_key)

    return {
        "status":   "success",
        "grant_id": grant_id,
        "grant":    match,
        "message":  f"Grant {grant_id} loaded from artifact"
    }


async def get_grants_by_employee_ids(
    employee_ids: List[str],
    tool_context: ToolContext
) -> Dict:
    """
    Returns grant summary for a list of employee_ids.
    Used by orchestrator for cross-agent joins.
    Returns keys and summaries only — never full records to orchestrator.
    Reads from artifact — no disk I/O after first load.

    Args:
        employee_ids: List of employee IDs to filter by

    LLM Prompt Examples:
      - 'Get grants for these employees'
      - 'Which grant types do these participants have?'
      - 'Show grant summary for this employee list'

    Returns:
      status, source, employee_ids, total_grants,
      grant_ids, by_employee (summary per employee), message
    """
    data = await _load_artifact(tool_context)
    if not data:
        await load_grants(tool_context)
        data = await _load_artifact(tool_context)

    matched = [
        g for g in data["grants"]
        if g["employee_id"] in employee_ids
    ]

    by_employee: Dict = {}
    for g in matched:
        emp_id = g["employee_id"]
        if emp_id not in by_employee:
            by_employee[emp_id] = {
                "employee_name": g["employee_name"],
                "grant_count":   0,
                "grant_types":   [],
                "grant_ids":     [],
                "total_unvested": 0,
            }
        by_employee[emp_id]["grant_count"]    += 1
        by_employee[emp_id]["total_unvested"] += g["unvested_shares"]
        if g["grant_type"] not in by_employee[emp_id]["grant_types"]:
            by_employee[emp_id]["grant_types"].append(g["grant_type"])
        by_employee[emp_id]["grant_ids"].append(g["grant_id"])

    all_grant_ids = [g["grant_id"] for g in matched]

    return {
        "status":       "success",
        "source":       "artifact",
        "employee_ids": employee_ids,
        "total_grants": len(matched),
        "grant_ids":    all_grant_ids,
        "by_employee":  by_employee,
        "message":      f"Found {len(matched)} grants for "
                        f"{len(by_employee)} employees"
    }
