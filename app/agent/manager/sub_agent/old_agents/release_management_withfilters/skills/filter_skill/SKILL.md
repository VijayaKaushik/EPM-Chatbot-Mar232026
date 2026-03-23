---
name: filter-skill
description: >
  Extract filter conditions from natural language and apply
  them to tranche data for subset processing.
---

# Filter Skill

## Purpose

Enables intelligent data subsetting by:
- Parsing natural language queries for filter intent
- Converting to structured filter conditions
- Applying filters to tranche data
- Reporting filtered results

## Two-Phase Workflow

### Phase 1: Filter Extraction
- **Tool**: `extract_filters_from_query`
- **Input**: User's natural language query
- **Process**: Uses Gemini LLM to parse intent
- **Output**: Structured FilterCondition objects

### Phase 2: Filter Application
- **Tool**: `apply_filter`
- **Input**: Vesting date + filter conditions from state
- **Process**: Evaluates each tranche against conditions
- **Output**: Filtered dataset stored in state

## Supported Filter Types

### Grant Type (Text Equality)
- **Values**: RSU, Stock Option, Restricted Stock, PSU
- **Example**: "Simulate RSUs" → `{field: "grant_type", operator: "=", value: "RSU"}`

### Shares Released (Numeric Comparison)
- **Operators**: >, <, >=, <=, =
- **Example**: "Grants above 10000" → `{field: "shares_released", operator: ">", value: 10000}`

### Department (Text Equality)
- **Values**: Engineering, Sales, Finance, Marketing, HR, Product, Operations
- **Example**: "Engineering team" → `{field: "department", operator: "=", value: "Engineering"}`

### Country (Text Equality)
- **Values**: Any country name
- **Example**: "US employees" → `{field: "country", operator: "=", value: "United States"}`

### Employee Status (Text Equality)
- **Values**: Active, Terminated
- **Example**: "Active employees" → `{field: "employee_status", operator: "=", value: "Active"}`

## Critical Rules

### ❌ NOT Filters (Parameters)
- **FMV** (Fair Market Value) - simulation parameter
- **Sales price** - simulation parameter

These do NOT subset data - they are used in tax calculation.

### ✅ Filters (Subset Data)
- Anything that reduces the number of records
- Conditions that select specific tranches

## Examples

### Example 1: Single Filter
```
Query: "Simulate RSUs"
Filters: grant_type = "RSU"
Result: Only RSU tranches processed
```

### Example 2: Multiple Filters (AND logic)
```
Query: "Engineering RSUs above 5000 shares"
Filters:
  - department = "Engineering"
  - grant_type = "RSU"
  - shares_released > 5000
Result: Only Engineering RSUs with >5000 shares
```

### Example 3: Filter + Parameters
```
Query: "Simulate Engineering RSUs with FMV 10"
Filters: department = "Engineering", grant_type = "RSU"
Parameters: FMV = 10
Result: Filter applied first, then tax calculated with FMV=10
```

### Example 4: No Filters (Parameters Only)
```
Query: "Simulate next vesting with FMV 10 and sales 12"
Filters: None
Parameters: FMV = 10, sales = 12
Result: All tranches processed with given FMV/sales
```

## Implementation Details

### Operator Evaluation
- `=`: Exact equality
- `!=`: Not equal
- `>`: Greater than (numeric)
- `<`: Less than (numeric)
- `>=`: Greater than or equal (numeric)
- `<=`: Less than or equal (numeric)
- `contains`: String contains (case-insensitive)

### Combination Logic
- Default: **AND** (all conditions must match)
- Future: Support for OR logic

### Error Handling
- Invalid field name → Error with available fields list
- No matching records → Clear error message
- LLM parse failure → Fallback to no filters

## State Management

### Filter Extraction Output
Stored in: `state["filter_conditions"]`
```python
{
  "has_filters": True,
  "conditions": [
    {"field": "grant_type", "operator": "=", "value": "RSU"}
  ],
  "filter_summary": "Grant type is RSU"
}
```

### Filtered Data Output
Stored in: `state["filtered_tranches"][vesting_date]`
```python
[
  {...tranche matching all conditions...},
  {...tranche matching all conditions...}
]
```

## Integration with Workflow

1. **After fetching data**: Call `extract_filters_from_query`
2. **Before tax calculation**: Call `apply_filter`
3. **Tax calculation**: Uses filtered data automatically
4. **Batch creation**: Includes filter summary in metadata
