import json
import os
import pathlib
from typing import Dict

import pandas as pd
from dotenv import load_dotenv
from pandasai.llm.base import LLM as _PaiLLM

load_dotenv()

PARTICIPANT_DATA_DIR = pathlib.Path(__file__).parent / "participant_data"


def get_all_participants() -> Dict:
    """
    Loads and returns all participant records from participants.json.

    Returns all records with no filtering — the agent and PandasAI handle
    all filtering, grouping, and aggregation downstream.

    Use this tool for:
    - "how many participants in US"
    - "group by KYC status"
    - "list all insiders"
    - "count by department"
    - "show terminated employees"
    - "list all participants"
    - "who is in blackout?"

    Returns:
        Dict containing:
            status (str): success or error
            total (int): Total number of participants
            participants (List[Dict]): All participant records
            message (str): Status message
    """
    path = PARTICIPANT_DATA_DIR / "participants.json"
    if not path.exists():
        return {
            "status": "error",
            "total": 0,
            "participants": [],
            "message": "participants.json not found",
        }
    data = json.loads(path.read_text())
    return {
        "status": "success",
        "total": len(data),
        "participants": data,
        "message": f"Retrieved {len(data)} participants",
    }


def get_participant_details(employee_id: str) -> Dict:
    """
    Returns full combined participant record for a given employee_id.

    Loads participant_details.json and performs an exact match on employee_id.
    Also loads the matching record from participants.json and merges it so the
    caller gets the complete picture in one call.

    Use this tool for:
    - "show me Taylor Randolph's details"
    - "get address for employee 74069291"
    - "what is the tax info for employee X"
    - "show account info for employee Y"

    Args:
        employee_id (str): Exact employee ID to look up.

    Returns:
        Dict containing:
            status (str): success or not_found
            employee_id (str): The requested employee ID
            participant (Dict): Merged record with all fields from both files
            message (str): Status message
    """
    details_path = PARTICIPANT_DATA_DIR / "participant_details.json"
    participants_path = PARTICIPANT_DATA_DIR / "participants.json"

    if not details_path.exists() or not participants_path.exists():
        return {
            "status": "error",
            "employee_id": employee_id,
            "message": "Participant data files not found",
        }

    details_data = json.loads(details_path.read_text())
    participants_data = json.loads(participants_path.read_text())

    detail_record = next((r for r in details_data if str(r["employee_id"]) == str(employee_id)), None)
    if detail_record is None:
        return {
            "status": "not_found",
            "employee_id": employee_id,
            "message": f"No participant found with employee_id={employee_id}",
        }

    base_record = next((r for r in participants_data if str(r["employee_id"]) == str(employee_id)), {})

    # Merge: base record fields + all detail fields
    combined = {**base_record, **detail_record}

    return {
        "status": "success",
        "employee_id": employee_id,
        "participant": combined,
        "message": f"Retrieved full details for employee {employee_id}",
    }


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


def analyze_participant_data(query: str) -> Dict:
    """
    Analyzes participant data using a natural language query powered by PandasAI.

    Loads both participants.json and participant_details.json, flattens all
    nested blobs (current_address, office_address, tax_info, account_info),
    merges on employee_id, and passes the resulting DataFrame to PandasAI.

    Flattened column mapping:
        current_address.city      → current_city
        current_address.state     → current_state
        current_address.country   → current_country
        office_address.city       → office_city
        office_address.country    → office_country
        tax_info.tax_residency    → tax_residency
        tax_info.withholding_rate → withholding_rate
        tax_info.w8_w9_status     → w8_w9_status
        account_info.account_status → account_status
        account_info.account_type   → account_type
        account_info.bank_name      → bank_name
        account_info.ach_status     → ach_status

    Use this tool for:
    - "How many participants by country?"
    - "List all insiders currently in blackout"
    - "Show KYC status breakdown"
    - "Which participants have expired W8/W9?"
    - "Count active vs terminated by department"
    - "Show participants with unverified ACH"
    - "Average withholding rate by country"
    - "How many are grant eligible?"
    - "Breakdown by employment status"

    Args:
        query (str): A natural language question about participant data.

    Returns:
        Dict containing:
            status (str): success or error
            query (str): The original query
            result (str): The analysis result from PandasAI
            total_rows (int): Number of rows in the merged dataset
            message (str): Status or error message
    """
    try:
        from pandasai.agent import Agent as PaiAgent

        participants_path = PARTICIPANT_DATA_DIR / "participants.json"
        details_path = PARTICIPANT_DATA_DIR / "participant_details.json"

        if not participants_path.exists() or not details_path.exists():
            return {
                "status": "error",
                "query": query,
                "result": None,
                "total_rows": 0,
                "message": "Participant data files not found",
            }

        participants_data = json.loads(participants_path.read_text())
        details_data = json.loads(details_path.read_text())

        # Flatten nested blobs from participant_details
        flat_details = []
        for rec in details_data:
            flat = {"employee_id": str(rec["employee_id"])}

            ca = rec.get("current_address", {})
            flat["current_city"] = ca.get("city")
            flat["current_state"] = ca.get("state")
            flat["current_country"] = ca.get("country")

            oa = rec.get("office_address", {})
            flat["office_city"] = oa.get("city")
            flat["office_country"] = oa.get("country")

            ti = rec.get("tax_info", {})
            flat["tax_residency"] = ti.get("tax_residency")
            flat["withholding_rate"] = ti.get("withholding_rate")
            flat["w8_w9_status"] = ti.get("w8_w9_status")

            ai = rec.get("account_info", {})
            flat["account_status"] = ai.get("account_status")
            flat["account_type"] = ai.get("account_type")
            flat["bank_name"] = ai.get("bank_name")
            flat["ach_status"] = ai.get("ach_status")

            flat_details.append(flat)

        participants_df = pd.DataFrame(participants_data)
        participants_df["employee_id"] = participants_df["employee_id"].astype(str)

        details_df = pd.DataFrame(flat_details)

        merged_df = participants_df.merge(details_df, on="employee_id", how="left")

        api_key = os.environ.get("GOOGLE_API_KEY", "")
        llm = GeminiLLM(api_key=api_key, model="gemini-2.5-flash")

        agent = PaiAgent(merged_df, config={"llm": llm})
        result = agent.chat(query)

        if isinstance(result, pd.DataFrame):
            result_str = result.to_markdown(index=False)
        elif isinstance(result, pd.Series):
            result_str = result.to_markdown()
        else:
            result_str = str(result)

        return {
            "status": "success",
            "query": query,
            "result": result_str,
            "total_rows": len(merged_df),
            "message": "Analysis completed successfully",
        }
    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "result": None,
            "total_rows": 0,
            "message": f"Analysis failed: {str(e)}",
        }
