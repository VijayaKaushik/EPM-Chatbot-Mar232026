---
name: vesting-schedule
description: >
  View upcoming equity vesting dates and retrieve participant details
  for a specific vesting date. Use for informational queries only —
  not for release processing. Covers RSU, PSU, and Stock Option grants.
  Supports flexible date filtering: next N dates, by month/year, date ranges.
---

# Vesting Schedule Skill

## When to Use
Informational queries only — viewing dates and participant summaries.
For release processing, batch creation, or tax calculation → use release-workflow skill.

## Workflow
[1] get_vesting_dates(client_id?, count?, month?, year?, start_date?, end_date?) → show dates
[2] get_vesting_details(vesting_date) → show participant summary

## Stage 1: Get Vesting Dates
Tool: get_vesting_dates(client_id="CLIENT_001", count=1, month=None, year=None, start_date=None, end_date=None)

### Query Patterns Supported:
- **Next N dates**: `count=3` → returns next 3 future vesting dates
- **All dates**: no parameters → returns all vesting dates for client
- **By month**: `month=6, year=2026` → returns all dates in June 2026
- **Date range**: `start_date="2026-05-01", end_date="2026-12-31"` → returns dates in range

### Examples:
- "Give me next vesting date" → `count=1`
- "Show me next 3 vesting dates" → `count=3`
- "What are vesting dates in June?" → `month=6`
- "Get vesting dates for May 2027" → `month=5, year=2027`
- "List vesting dates from May to December 2026" → `start_date="2026-05-01", end_date="2026-12-31"`
- "Get all vesting dates" → no filters

### Response Format:
```json
{
  "status": "success",
  "vesting_dates": ["2026-05-15", "2026-06-15"],
  "client_id": "CLIENT_001",
  "filter_type": "next_2",
  "total_found": 2,
  "message": "Retrieved 2 vesting date(s) for CLIENT_001 (next_2)"
}
```

- Show dates in a clean list with filter type
- Ask which date to view details for

## Stage 2: Get Vesting Details
Tool: get_vesting_details(vesting_date, tool_context)
- Present participant table: employee, grant type, shares, net value, status
- Show total count and summary
- Never expose token_id to user