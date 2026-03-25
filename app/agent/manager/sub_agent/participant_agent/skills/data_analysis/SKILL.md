---
name: participant-data-analysis
description: >
  Analyze, aggregate, group, count, filter, and summarize equity plan participant
  data using natural language queries. Supports analysis by country, department,
  employment status, insider status, blackout status, KYC status, tax residency,
  withholding rate, ACH status, account status, W8/W9 status, and grant eligibility.
  Powered by PandasAI on a merged dataset from participants.json and participant_details.json.
---

# Participant Data Analysis Skill

## Overview

This skill handles analytical queries against the full participant dataset. It uses
`analyze_participant_data(query)` to run natural language analysis via PandasAI on a
merged, flattened DataFrame combining summary and detail records.

## Workflow

```
[1] analyze_participant_data(query) → run analysis via PandasAI
[2] Present results as table or summary
```

---

## Tool

**`analyze_participant_data(query)`**

```python
def analyze_participant_data(query: str) -> Dict:
```

**Args:**
- `query` (str): Natural language question about participant data

**Returns:**
```json
{
  "status": "success",
  "query": "How many participants by country?",
  "result": "| country_of_residence | count |\n|---|---|\n| United States | 12 |",
  "total_rows": 50,
  "message": "Analysis completed successfully"
}
```

---

## Available Columns (after flattening and merge)

### From participants.json
| Column | Description |
|---|---|
| `employee_id` | Unique employee identifier |
| `full_name` | Full name of the participant |
| `country_of_residence` | Country where participant resides |
| `employment_status` | Active, Terminated, On Leave |
| `insider_status` | Insider, Non-Insider |
| `blackout_status` | In Blackout, Not in Blackout |
| `kyc_status` | Verified, Expired, Pending |
| `broker_code` | Broker code (show only if explicitly requested) |
| `officer_code` | Officer code (show only if explicitly requested) |
| `client_id` | Client identifier |
| `department` | Department name (Finance, Engineering, Sales, etc.) |
| `job_title` | Job title |
| `grant_eligible` | Boolean — eligible for equity grants |

### From participant_details.json (flattened)
| Column | Description |
|---|---|
| `current_city` | Current address city |
| `current_state` | Current address state |
| `current_country` | Current address country |
| `office_city` | Office address city |
| `office_country` | Office address country |
| `tax_residency` | US Resident, Non-US Resident |
| `withholding_rate` | Tax withholding rate (decimal, e.g. 0.22) |
| `w8_w9_status` | W8-BEN on file, W9 on file, Expired, Missing |
| `account_status` | Active, Inactive, Suspended |
| `account_type` | Individual, Joint, Trust |
| `bank_name` | Bank name for ACH |
| `ach_status` | Verified, Unverified, Pending |

---

## Example Queries

- "How many participants by country?"
- "List all insiders currently in blackout"
- "Show KYC status breakdown"
- "Which participants have expired W8/W9?"
- "Count active vs terminated by department"
- "Show participants with unverified ACH"
- "Average withholding rate by country"
- "How many are grant eligible?"
- "Show all participants in blackout period"
- "Breakdown by employment status"
- "Which departments have the most insiders?"
- "Count participants by tax residency type"
- "Show participants where account_status is Inactive"
- "How many participants have W9 on file vs W8-BEN?"

---

## Presentation Rules

- Present tabular results as markdown tables
- Format withholding_rate as percentage (e.g. 0.22 → 22%)
- Never display raw tax_id — always mask as XXX-XX-XXXX
- Only show broker_code / officer_code if user explicitly requests them
- Provide a brief plain-language summary after every table

---

## Error Handling

- If PandasAI returns an error: report clearly with the query that failed
- If data files not found: "Participant data is unavailable. Please contact support."
- If result is empty: "No participants match those criteria."
