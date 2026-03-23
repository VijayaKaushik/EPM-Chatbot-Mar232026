# Tax Calculation Skill

## Overview
Calculate vesting taxes through a 4-stage workflow implemented as LangGraph nodes.

## Nodes

### 1. get_dates_node
- Retrieves available vesting dates
- Presents options to user
- Transitions to: `get_details_node`

### 2. get_details_node
- Creates token for selected date
- Stores in state: `token_vesting_list`
- Shows participant summary
- Transitions to: `collect_inputs_node`

### 3. collect_inputs_node
- Collects FMV and sales price
- Validates inputs are positive
- Transitions to: `calculate_tax_node`

### 4. calculate_tax_node
- Validates token exists in state
- Calculates tax using FMV and sales price
- Returns summary and approval URL
- Transitions to: `END`

## State Requirements

```python
{
    "token_vesting_list": [(vesting_date, token_id)],
    "current_vesting_date": str,
    "fmv": float,
    "sales_price": float,
    "workflow_stage": str
}
```

## Tools Used

- `get_vesting_dates(count: int)`
- `get_vesting_details(vesting_date: str)`
- `calculate_tax(vesting_date: str, fmv: float, sales: float, token_id: str)`
