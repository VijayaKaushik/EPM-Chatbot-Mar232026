---
name: participant-lookup
description: >
  Look up equity plan participants by name or employee ID. Retrieve full participant
  profiles including address, tax information, account status, KYC status, insider
  status, blackout status, broker details, and grant eligibility. Supports searching
  by full name or exact employee ID, and returns merged records from both participant
  summary and detail data sources.
---

# Participant Lookup Skill

## Overview

This skill guides users through finding a specific participant by name or employee ID
and retrieving their full combined profile. It covers two lookup paths: searching by
name (requires listing all participants first) and direct lookup by employee ID.

## Workflow Stages

```
[1] DETERMINE QUERY TYPE → Aggregation or specific person lookup
[2a] AGGREGATION / GROUP / COUNT → analyze_participant_data(query)
[2b] SPECIFIC PERSON by name → get_all_participants → find employee_id → get_participant_details
[2c] SPECIFIC PERSON by employee_id → get_participant_details(employee_id) directly
[3] PRESENT RESULTS → Clean, business-friendly table or summary
```

---

## Decision Logic

| Query pattern | Path |
|---|---|
| Contains a name ("Taylor", "Marcus Chen") | 2b — name lookup |
| Contains an employee ID ("74069291") | 2c — direct ID lookup |
| "how many", "group", "count", "breakdown", "aggregate" | 2a — analysis |
| "who is", "show all", "list participants" | get_all_participants |

---

## Stage 2a: Aggregation / Group / Count

### Tool
**`analyze_participant_data(query)`**

Use this path when the user wants to aggregate, count, filter, or group across
the full participant population. Do not use get_all_participants for these queries —
go directly to analyze_participant_data.

Examples:
- "how many participants are in the US?"
- "group by KYC status"
- "list all insiders"
- "count by department"
- "breakdown by employment status"

---

## Stage 2b: Specific Person by Name

### Step 1 — Resolve employee_id
**`get_all_participants()`**

```python
def get_all_participants() -> Dict:
```

Returns all participant summary records. Scan the returned list to find the
employee_id for the person named by the user. If multiple matches exist,
ask the user to confirm which one.

### Step 2 — Fetch full details
**`get_participant_details(employee_id)`**

```python
def get_participant_details(employee_id: str) -> Dict:
```

Returns the full merged record: all fields from participants.json plus all
detail fields from participant_details.json (addresses, tax_info, account_info).

---

## Stage 2c: Specific Person by Employee ID

### Tool
**`get_participant_details(employee_id)`**

Call directly with the employee_id provided by the user. No need to call
get_all_participants first.

---

## Stage 3: Present Results

### Instructions

Present results as a clean business-friendly table or structured summary.

**For a single participant — full profile:**
```
Participant Profile: Taylor Randolph (74069291)

| Field              | Value                        |
|--------------------|------------------------------|
| Full Name          | Taylor Randolph              |
| Employee ID        | 74069291                     |
| Department         | Finance                      |
| Job Title          | Senior Analyst               |
| Employment Status  | Active                       |
| Country            | Japan                        |
| KYC Status         | Verified                     |
| Insider Status     | Non-Insider                  |
| Blackout Status    | Not in Blackout              |
| Grant Eligible     | Yes                          |
| Tax Residency      | Non-US Resident              |
| Withholding Rate   | 20%                          |
| W8/W9 Status       | W8-BEN on file               |
| Account Status     | Active                       |
| Account Type       | Individual                   |
| Bank               | MUFG Bank                    |
| ACH Status         | Verified                     |
| Current City       | Port Lindachester            |
| Current State      | Michigan                     |
| Current Country    | Japan                        |
```

**Sensitivity rules:**
- `tax_id` always shown masked: **XXX-XX-XXXX** — never display the raw value
- `broker_code` and `officer_code` only shown if user explicitly asks for them
- Never expose raw account numbers

---

## Error Handling

- If name matches multiple participants: present a small table and ask user to confirm
- If employee_id not found: "No participant found with that employee ID. Please verify and try again."
- If participant data files are missing: report the error clearly
