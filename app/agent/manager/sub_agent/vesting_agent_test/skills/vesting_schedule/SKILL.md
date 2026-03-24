---
name: vesting-schedule
description: >
  View upcoming equity vesting dates, retrieve detailed participant vesting
  records including shares released, FMV, tax method, and delivery status
  for a specific vesting date. Supports RSU, PSU, and Stock Option grants.
---

# Vesting Schedule Skill

## Overview

This skill guides users through viewing upcoming vesting dates and retrieving
detailed participant information for a specific vesting event. It uses a two-stage
workflow: first showing available dates, then fetching details for a selected date.

## Workflow Stages

```
[1] GET VESTING DATES → Show upcoming dates → Ask which date(s) to view
[2] GET VESTING DETAILS → Retrieve participant records → Display summary
```

---

## Stage 1: Get Vesting Dates

### Tool
**`get_vesting_dates(count)`**

```python
def get_vesting_dates(count: Optional[int] = 1) -> Dict:
```

**Args:**
- `count` (int, optional): Number of upcoming vesting dates to return. Defaults to 1.

**Returns:**
```json
{
  "status": "success",
  "vesting_dates": ["2026-03-15", "2026-06-15", ...]
}
```

### Instructions
1. Ask the user how many upcoming vesting dates they want to see (or default to 1)
2. Call `get_vesting_dates(count)` with the requested count
3. Present the dates clearly:
   ```
   Here are your upcoming vesting dates:
   1. 2026-03-15
   2. 2026-06-15
   ```
4. Ask: "Which date would you like to see details for?"
5. If user selects a date, proceed to Stage 2

### Validation
- `count` must be a positive integer
- If user asks for more dates than available, return all available dates

---

## Stage 2: Get Vesting Details

### Tool
**`get_vesting_details(vesting_date, tool_context)`**

```python
def get_vesting_details(vesting_date: str, tool_context: ToolContext) -> Dict:
```

**Args:**
- `vesting_date` (str): Vesting date in YYYY-MM-DD format
- `tool_context` (ToolContext): ADK tool context for state management

**State Side Effects:**
- Reads `tool_context.state["token_vesting_list"]` (may be None initially)
- Appends `(vesting_date, token_id)` tuple to the list
- Writes updated list back to `tool_context.state["token_vesting_list"]`

**Returns:**
```json
{
  "status": "success",
  "vesting_date": "2026-03-15",
  "token_id": "token_a1b2c3d4",
  "participants": [
    {
      "employee_id": "74069291",
      "employee_name": "Taylor Randolph",
      "department": "Finance",
      "grant_type": "RSU",
      "shares_released": 1522,
      "net_shares_delivered": 993,
      "fmv_at_release": 526094.52,
      "net_value_delivered": 343240.38,
      "release_status": "Completed"
    }
  ],
  "message": "Token and participant details retrieved successfully"
}
```

### Instructions
1. Call `get_vesting_details(vesting_date, tool_context)` with the selected date
2. **IMPORTANT: Never expose `token_id` to the user** — it is for internal state only
3. Present participant data as a business-friendly summary:
   ```
   Vesting Details for 2026-03-15:

   | Employee        | Dept        | Grant Type    | Shares Released | Net Delivered | Net Value     | Status    |
   |-----------------|-------------|---------------|-----------------|---------------|---------------|-----------|
   | Taylor Randolph | Finance     | RSU           | 1,522           | 993           | $343,240.38   | Completed |
   | Marcus Chen     | Engineering | PSU           | 834             | 517           | $149,634.31   | Completed |
   | Sophia Alvarez  | Sales       | Stock Option  | 2,000           | 1,240         | $387,500.00   | Pending   |
   ```
4. Provide a brief summary: total participants, total shares, overall status
5. Ask if the user wants to view details for another date or needs anything else

### Validation
- `vesting_date` must be in YYYY-MM-DD format
- Verify the date is one of the available vesting dates from Stage 1

---

## State Management

### `token_vesting_list`
- **Type**: `List[Tuple[str, str]]` — list of `(vesting_date, token_id)` pairs
- **Set by**: `get_vesting_details`
- **Scope**: Session state via `tool_context.state`
- **Purpose**: Tracks which vesting dates have been queried and their associated tokens
- **Rule**: `token_id` is strictly internal — never display to users

---

## Error Handling

- If `get_vesting_dates` returns empty list: "There are no upcoming vesting dates at this time."
- If user provides invalid date format: "Please provide the date in YYYY-MM-DD format."
- If user selects a date not in the available list: "That date isn't in the upcoming vesting schedule. Here are the available dates: ..."
