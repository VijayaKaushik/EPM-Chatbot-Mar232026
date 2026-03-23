---
name: vesting-tax-calculation
description: >
  Calculate vesting taxes through a guided workflow: fetch dates, get details,
  collect FMV/sales price, and generate tax summary with approval URL.
---

# Vesting Tax Calculation

## Workflow

```
[1] get_vesting_dates → Show available dates
[2] get_vesting_details → Create token, store in state
[3] Collect FMV & sales price → Validate inputs
[4] calculate_tax → Present summary + approval URL
```

---

## Stage 1: Get Vesting Dates

**Tool**: `get_vesting_dates(count: int = 1)`

1. Parse `count` from user message (default: 1)
2. Call tool and display dates
3. Ask which date(s) to process

---

## Stage 2: Get Vesting Details

**Tool**: `get_vesting_details(vesting_date: str, tool_context: ToolContext)`

1. Call for selected date - creates `token_id` and stores in `state["token_vesting_list"]`
2. Confirm token created and show participant summary
3. Proceed to collect FMV/sales price

**Critical**: Must complete before Stage 4. Token required for tax calculation.

---

## Stage 3: Collect FMV & Sales Price

**Tool**: None

1. Ask for FMV and sales price if not provided
2. Validate both are positive numbers
3. Confirm values before proceeding

---

## Stage 4: Calculate Tax

**Tool**: `calculate_tax(vesting_date: str, fmv: float, sales: float, tool_context: ToolContext)`

1. Verify `vesting_date` exists in `state["token_vesting_list"]`
2. Call tool with validated parameters
3. Present summary and approval URL

**Error Recovery**: If token missing, call `get_vesting_details` first, then retry.

---

## State

State stores `token_vesting_list` as `List[Tuple[vesting_date, token_id]]`

- Set by: `get_vesting_details`
- Used by: `calculate_tax`
- Must exist before calculating tax

---

## Tools

**get_vesting_dates(count: int = 1)**
- Returns: `{status, vesting_dates: List[str]}`

**get_vesting_details(vesting_date: str, tool_context: ToolContext)**
- Returns: `{status, vesting_date, token_id, message}`
- Side effect: Appends to `state["token_vesting_list"]`

**calculate_tax(vesting_date: str, fmv: float, sales: float, tool_context: ToolContext)**
- Returns: `{status, vesting_date, summary, approval_url, message}`
- Requires: Token in state for vesting_date

---

## Guidelines

- Never skip Stage 2 before Stage 4
- Never expose token_id to users
- Validate FMV and sales price are positive
- If token missing at Stage 4, create it then retry
- Present results clearly with approval URL
