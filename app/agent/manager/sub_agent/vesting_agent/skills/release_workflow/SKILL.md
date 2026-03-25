---
name: release-workflow
description: >
  Guide admin through the full equity release workflow for a vesting date.
  Handles participant filtering by grant type, officer status, or tax method,
  tax calculation with user-provided FMV and sales price, batch creation,
  and approval URL generation. Supports multiple batches per vesting date.
  Works with unbatched participants only. Enforces strict stage ordering:
  filter → tax calculation → batch creation.
---

# Release Workflow Skill

## Overview

This skill walks an admin through creating one or more release batches for a vesting date.
It enforces a strict stage order: filter participants first, then calculate tax, then create
the batch. Multiple batches can be created for the same vesting date — each run works
exclusively on the remaining unbatched participants.

## Workflow Stages

```
[1] GET VESTING DATE        → get_vesting_dates(count=1)
[2] GET VESTING DETAILS     → get_vesting_details(vesting_date)
[3] COLLECT FILTERS         → conversational only
[4] FILTER PARTICIPANTS     → filter_participants(vesting_date, ...)
[5] COLLECT FMV / PRICE     → conversational only
[6] CALCULATE TAX           → calculate_tax_for_batch(fmv, sales_price)
[7] CREATE BATCH            → create_batch()
```

---

## Stage 1: Get Vesting Date

### Tool
**`get_vesting_dates(count=1)`**

### Instructions
- If admin already mentioned the date in their message, use it directly — skip this stage
- Otherwise call `get_vesting_dates(count=1)` and present the next upcoming date
- Confirm with admin: "The next vesting date is YYYY-MM-DD. Would you like to proceed with this date?"

---

## Stage 2: Get Vesting Details

### Tool
**`get_vesting_details(vesting_date)`**

### Instructions
- Call `get_vesting_details(vesting_date)` to load participants into state
- Present a summary: total participant rows, breakdown by grant type
- **Never expose token_id to the admin**
- Example output:
  ```
  Vesting Date: 2026-05-15
  Total participants: 13 rows (including multi-tranche)
  Unbatched: 13
  ```

---

## Stage 3: Collect Filters (conversational)

### Tool
None — conversational only

### Instructions
- Filters are **optional**. The default is to include all unbatched participants.
- If admin already stated a filter in their opening message, apply it directly in Stage 4 without asking again.
- Otherwise ask a single yes/no question:
  ```
  Would you like to apply any filters, or shall I proceed with all X unbatched participants?

  Optional filters available:
  1. Grant type     — RSU / PSU / Stock Option
  2. Officer status — Officer / Non-Officer
  3. Tax method     — Net Issuance / Sell-to-Cover / Cash Payment
  ```
- If admin says **no / proceed / all / include all** → call `filter_participants` with no filter arguments (all unbatched participants included)
- If admin specifies a filter → apply it, then ask: "Any additional filters, or shall we proceed?"
- Once admin confirms (or declines filters), proceed immediately to Stage 4 — do not ask again

---

## Stage 4: Filter Participants

### Tool
**`filter_participants(vesting_date, grant_type, officer_status, tax_method)`**

```python
def filter_participants(
    vesting_date: str,
    grant_type: Optional[str] = None,
    officer_status: Optional[str] = None,
    tax_method: Optional[str] = None,
    tool_context: ToolContext = None,
) -> Dict:
```

### Instructions
1. Call with the confirmed filter values (omit filters not selected)
2. Present the filtered participant table:
   ```
   | Employee        | Grant Type | Officer Status | Tax Method     | Shares |
   |-----------------|------------|----------------|----------------|--------|
   | Taylor Randolph | RSU        | Non-Officer    | Net Issuance   | 913    |
   | Lin Zhang       | RSU        | Non-Officer    | Net Issuance   | 630    |
   ```
3. Show counts:
   ```
   Matched:  X participants
   Unbatched total: Y
   Remaining after this batch: Z
   ```
4. Ask: "Does this look correct? Shall I calculate tax for these participants?"

### Error handling
- `status: no_match` → "No unbatched participants match those filters. Try different criteria or choose 'No filter'."

---

## Stage 5: Collect FMV and Sales Price (conversational)

### Tool
None — conversational only

### Instructions
Ask:
```
Please provide the following values for tax calculation:
- FMV (Fair Market Value per share)
- Sales price per share
```
- Both values must be positive numbers
- Sell-to-Cover: ask for both FMV and sales price
- Net Issuance, Withhold to Cover, or Cash Payment: ask for FMV only
  sales price defaults to FMV value — do not ask admin
- Confirm before moving on: "FMV: $X.XX, Sales price: $Y.YY — shall I calculate tax?"

---

## Stage 6: Calculate Tax

### Tool
**`calculate_tax_for_batch(fmv, sales_price)`**

```python
def calculate_tax_for_batch(fmv: float, sales_price: float, tool_context: ToolContext) -> Dict:
```

### Instructions
1. Call with the confirmed FMV and sales price
2. Present the tax summary table:

   | Metric                  | Value       |
   |-------------------------|-------------|
   | Total participants      | X           |
   | Total shares released   | X           |
   | Total FMV               | $X,XXX.XX   |
   | Total tax withheld      | $X,XXX.XX   |
   | Net value delivered     | $X,XXX.XX   |

3. Ask: "Tax calculation complete. Ready to create the batch and generate the approval URL?"

---

## Stage 7: Create Batch

### Tool
**`create_batch()`**

```python
def create_batch(tool_context: ToolContext) -> Dict:
```

### Instructions
1. Call `create_batch()` — no arguments needed (reads everything from state)
2. Present batch confirmation:

   | Field              | Value                            |
   |--------------------|----------------------------------|
   | Batch ID           | BATCH-XXXXXXXX                   |
   | Vesting Date       | YYYY-MM-DD                       |
   | Participants       | X                                |
   | Total Tax Withheld | $X,XXX.XX                        |
   | Net Value          | $X,XXX.XX                        |
   | Approval URL       | https://approval.dummy.com/...   |

3. Inform admin of remaining unbatched participants:
   ```
   X participant rows remain unbatched for YYYY-MM-DD.
   ```
4. If remaining > 0, ask:
   ```
   Would you like to create another batch for the remaining X participants?
   ```
   - If yes: return to Stage 3 (collect new filters for the remaining participants)
   - If no: "Release workflow complete for YYYY-MM-DD."

---

## Critical Rules

1. **Always call filter_participants before calculate_tax_for_batch** — even with no filters selected, call `filter_participants(vesting_date)` with no filter args to load all unbatched participants into state. Filters are optional; this tool call is not.
2. **Never skip Stage 6 (tax) before Stage 7 (batch)** — batch requires tax state
3. **Always show participant count at each stage**
4. **Always show remaining unbatched count after batch creation**
5. **If admin states filter in opening message, apply it in Stage 3 without asking again**
6. **Never expose token_id to admin**
7. **batch_id is shown to admin — it is not sensitive**
8. **Each create_batch call clears state** — a new filter_participants call is required for each subsequent batch

---

## Error Handling

- Filter returns no match → suggest different filter or "no filter" option
- CSV not found → "No vesting data available for that date"
- Missing state in calculate_tax_for_batch → "Please call filter_participants first"
- Missing state in create_batch → "Please complete tax calculation before creating the batch"
