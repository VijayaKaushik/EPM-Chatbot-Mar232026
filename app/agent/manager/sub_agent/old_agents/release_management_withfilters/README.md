# Release Management with Filters Agent

Enhanced release management agent with execution planning, smart filtering, and batch creation capabilities.

## Quick Start

```python
from app.agent.manager.sub_agent.old_agents.release_management_withfilters import root_agent

# Example 1: Simple simulation
response = root_agent.run("Simulate next vesting with FMV 10 and sales 12")

# Example 2: Filtered simulation
response = root_agent.run("Simulate RSUs for Engineering with FMV 10")

# Example 3: Complex filters
response = root_agent.run("Process grants above 5000 shares for active employees")
```

## Features

### 🎯 Execution Planning
- Creates structured plan before execution
- Detects filters vs parameters automatically
- Shows step-by-step workflow to user
- Validates prerequisites at each step

### 🔍 Smart Filtering
- Extracts filters from natural language
- Supports multiple filter types:
  - **Grant type**: RSU, Stock Option, Restricted Stock, PSU
  - **Shares**: Numeric comparisons (>, <, >=, <=, =)
  - **Department**: Engineering, Sales, Finance, etc.
  - **Country**: Any country name
  - **Status**: Active, Terminated
- Uses LLM to parse user intent
- Graceful fallback if parsing fails

### 📦 Batch Creation
- Generates unique batch ID
- Creates comprehensive metadata
- Includes filter traceability
- Saves as JSON file
- Provides approval URL
- Calculates net shares and proceeds

## Workflow

```
┌─────────────────────────────────────────────┐
│ 1. Create Execution Plan                   │
│    - Analyze query                          │
│    - Detect filters & parameters            │
│    - Build step sequence                    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 2. Fetch Vesting Details                   │
│    - Load from JSON or generate mock       │
│    - Store in state                         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
        ┌─────────┴─────────┐
        │  Filters detected? │
        └─────────┬─────────┘
                  │
         ┌────────┴────────┐
         │ YES             │ NO
         ▼                 │
┌─────────────────┐        │
│ 3. Extract      │        │
│    Filters      │        │
└────────┬────────┘        │
         │                 │
         ▼                 │
┌─────────────────┐        │
│ 4. Apply        │        │
│    Filters      │        │
└────────┬────────┘        │
         │                 │
         └────────┬────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 5. Calculate Tax                            │
│    - Use filtered or all data               │
│    - Apply FMV and sales price              │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 6. Create Batch                             │
│    - Generate batch ID                      │
│    - Create metadata                        │
│    - Save JSON file                         │
│    - Provide approval URL                   │
└─────────────────────────────────────────────┘
```

## Example Usage

### Example 1: Basic Simulation
```python
# User: "Simulate next vesting"
# Agent asks for FMV and sales price
# User: "FMV 10, sales 12"

# Result:
# ✅ Batch created successfully!
# Batch ID: BATCH_A1B2C3D4
# Records: 50 employees
# Total Shares: 250,000
# Total Tax: $875,000
# Approval URL: https://dummy.com/batches/BATCH_A1B2C3D4/approve
```

### Example 2: Filtered by Grant Type
```python
# User: "Simulate RSUs with FMV 10 and sales 12"

# Result:
# ✅ Batch created successfully!
# Batch ID: BATCH_E5F6G7H8
# Filtered Records: 20 RSU grants (out of 50 total)
# Total Shares: 100,000
# Total Tax: $350,000
# Filter Applied: Grant type is RSU
# Approval URL: https://dummy.com/batches/BATCH_E5F6G7H8/approve
```

### Example 3: Multiple Filters
```python
# User: "Engineering RSUs above 5000 shares with FMV 10"

# Filters applied:
# - department = "Engineering"
# - grant_type = "RSU"
# - shares_released > 5000

# Result:
# ✅ Batch created successfully!
# Batch ID: BATCH_I9J0K1L2
# Filtered Records: 8 grants (out of 50 total)
# Total Shares: 45,000
# Total Tax: $157,500
# Filter Applied: Department is Engineering AND Grant type is RSU AND Shares > 5000
```

## File Structure

```
release_management_withfilters/
├── __init__.py                     # Package initialization
├── agent.py                        # Agent configuration
├── models.py                       # Pydantic models
├── tool.py                         # Tool implementations
├── .env                           # Environment variables
├── README.md                       # This file
├── IMPLEMENTATION_SUMMARY.md       # Implementation details
└── skills/
    ├── planning_skill/
    │   └── SKILL.md               # Planning workflow docs
    ├── filter_skill/
    │   └── SKILL.md               # Filter extraction docs
    └── batch_creation_skill/
        └── SKILL.md               # Batch creation docs
```

## Tools Available

### Core Tools

1. **get_vesting_dates(count: int = 1)**
   - Returns upcoming vesting dates
   - Example: `get_vesting_dates(3)` → next 3 dates

2. **get_vesting_details_with_data(vesting_date: str)**
   - Loads tranche data from JSON or generates mock
   - Stores in state for processing

3. **create_execution_plan(vesting_date: str, user_query: str)**
   - Analyzes query and creates execution plan
   - Detects filters and parameters
   - Returns step sequence

4. **extract_filters_from_query(user_query: str)**
   - Uses LLM to parse natural language
   - Converts to structured FilterCondition objects
   - Distinguishes filters from parameters

5. **apply_filter(vesting_date: str)**
   - Applies filter conditions to tranche data
   - Uses AND logic for multiple conditions
   - Returns filtered dataset

6. **calculate_tax_with_filters(vesting_date: str, fmv: float, sales: float)**
   - Calculates tax for tranches
   - Works with filtered or unfiltered data
   - Tax rate: 35%
   - Formula:
     - gross_value = shares × fmv
     - tax_amount = gross_value × 0.35
     - net_proceeds = (shares × sales) - tax_amount

7. **create_batch(vesting_date: str, save_to_file: bool = True)**
   - Creates release batch from tax results
   - Generates unique batch_id
   - Creates metadata with totals
   - Saves JSON file
   - Provides approval URL

## State Management

The agent maintains state across tool calls:

```python
state = {
    "token_vesting_list": [
        ("2026-03-15", "token_a1b2c3d4"),
        ...
    ],

    "tranche_data": {
        "2026-03-15": [
            {employee_id, grant_type, shares_released, ...},
            ...
        ]
    },

    "execution_plan": {
        "plan_id": "PLAN_ABC123",
        "vesting_date": "2026-03-15",
        "steps": [...],
        "has_filters": True,
        "fmv_value": 10.0,
        "sales_value": 12.0
    },

    "filter_conditions": {
        "has_filters": True,
        "conditions": [
            {"field": "grant_type", "operator": "=", "value": "RSU"}
        ],
        "filter_summary": "Grant type is RSU"
    },

    "filtered_tranches": {
        "2026-03-15": [filtered_tranche_objects...]
    },

    "tax_results": {
        "2026-03-15": [tax_result_objects...]
    },

    "batches": {
        "BATCH_ABC123": {
            "metadata": {...},
            "records": [...]
        }
    }
}
```

## Batch Output Format

Batches are saved as JSON files:

**Filename**: `batch_{batch_id}_{vesting_date}.json`

**Structure**:
```json
{
  "metadata": {
    "batch_id": "BATCH_A1B2C3D4",
    "vesting_date": "2026-03-15",
    "creation_timestamp": "2026-03-19T10:30:00Z",
    "record_count": 20,
    "total_shares_released": 100000,
    "total_tax_withheld": 350000.00,
    "filter_applied": true,
    "filter_summary": "Grant type is RSU",
    "status": "pending_approval"
  },
  "records": [
    {
      "employee_id": "EMP001",
      "employee_name": "John Doe",
      "grant_type": "RSU",
      "shares_released": 5000,
      "fmv_at_release": 10.0,
      "sale_price_at_release": 12.0,
      "tax_withheld_amount": 17500.00,
      "net_shares_delivered": 3542,
      "net_proceeds": 42500.00
    },
    ...
  ]
}
```

## Filter vs Parameter

### Filters (Subset Data)
These reduce the number of records:
- `grant_type = "RSU"`
- `shares_released > 10000`
- `department = "Engineering"`
- `country = "United States"`
- `employee_status = "Active"`

### Parameters (Simulation Inputs)
These are used in calculations:
- `FMV = 10.0` (Fair Market Value)
- `sales = 12.0` (Sale price)

**Example**:
- ✅ "Simulate RSUs with FMV 10" → Filter: RSU, Parameter: FMV=10
- ✅ "Simulate with FMV 10" → No filter, Parameter: FMV=10
- ✅ "Engineering grants" → Filter: Engineering, Parameters: (ask user)

## Error Handling

### Missing Prerequisites
If tools are called out of order, you get clear errors:
```
Error: Vesting details not loaded for 2026-03-15.
Call get_vesting_details_with_data first.
```

### No Matching Records
If filters are too restrictive:
```
Error: No tranches match filter conditions.
Adjust filters or process all records.
```

### Invalid Field
If unknown filter field is used:
```
Error: Unknown field 'invalid_field'.
Available fields: grant_type, shares_released, department, country, employee_status.
```

## Dependencies

Required Python packages:
- `pydantic` - Data validation
- `google-adk` - Agent Development Kit
- `google-generativeai` - Gemini LLM for filter extraction
- `python-dotenv` - Environment variable loading

Install with:
```bash
pip install pydantic google-adk google-generativeai python-dotenv
```

## Configuration

Environment variables in `.env`:
```bash
GOOGLE_API_KEY=your_api_key_here
```

## Testing

Run tests (when dependencies are installed):
```bash
# Run all tests
python test_release_management_withfilters.py

# Or with pytest
pytest tests/
```

## Troubleshooting

### "No module named 'google.adk'"
Install dependencies: `pip install google-adk`

### "API key not found"
Set `GOOGLE_API_KEY` in `.env` file

### "Tranche data not found"
Place JSON files in parent directory or let agent generate mock data

### "Filter extraction failed"
Agent will fall back to processing all records without filters

## Performance

- **Filter extraction**: ~1-2 seconds (LLM call)
- **Data loading**: <1 second (JSON) or ~1 second (mock generation)
- **Tax calculation**: <1 second for 50 records
- **Batch creation**: <1 second
- **Total workflow**: ~3-5 seconds

## Limitations

- AND logic only (no OR for multiple filters)
- Fixed 35% tax rate (not configurable)
- Mock data generated per request (not persisted)
- Filter extraction depends on LLM availability

## Future Enhancements

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md#future-enhancements) for planned features.

## Support

For issues or questions:
1. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for detailed implementation info
2. Review skill documentation in `skills/*/SKILL.md`
3. Examine test cases in `test_release_management_withfilters.py`

## License

Part of the PythonProject application.
