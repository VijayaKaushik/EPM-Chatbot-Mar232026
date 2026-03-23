---
name: batch-creation-skill
description: >
  Create structured release batches from tax calculation results
  with metadata for approval workflows.
---

# Batch Creation Skill

## Purpose

Generates structured release batches ready for approval and execution. Provides:
- Unique batch identification
- Comprehensive metadata (totals, counts, timestamps)
- Individual employee records with tax calculations
- Filter traceability
- Approval workflow integration

## Workflow

1. **Validate tax results** - Ensure calculate_tax_with_filters completed
2. **Generate batch_id** - Create unique identifier
3. **Calculate totals** - Aggregate shares, tax amounts
4. **Create metadata** - Capture batch summary information
5. **Build records** - Convert tax results to batch records
6. **Save to file** - Write JSON file (optional)
7. **Generate approval URL** - Provide workflow link
8. **Store in state** - Save batch for reference

## Batch Structure

### Metadata Section
```json
{
  "batch_id": "BATCH_A1B2C3D4",
  "vesting_date": "2026-03-15",
  "creation_timestamp": "2026-03-19T10:30:00Z",
  "record_count": 25,
  "total_shares_released": 125000,
  "total_tax_withheld": 437500.00,
  "filter_applied": true,
  "filter_summary": "Grant type is RSU AND Department is Engineering",
  "status": "pending_approval"
}
```

### Records Section
```json
{
  "records": [
    {
      "employee_id": "A1B2C3D4",
      "employee_name": "John Smith",
      "grant_type": "RSU",
      "shares_released": 5000,
      "fmv_at_release": 10.0,
      "sale_price_at_release": 11.0,
      "tax_withheld_amount": 17500.00,
      "net_shares_delivered": 3409,
      "net_proceeds": 37500.00
    }
  ]
}
```

## Key Calculations

### Net Shares Delivered
```
shares_sold_for_tax = tax_withheld_amount / sale_price_at_release
net_shares_delivered = shares_released - shares_sold_for_tax
```

This represents the actual shares the employee receives after sell-to-cover tax withholding.

### Net Proceeds
```
net_proceeds = (shares_released × sale_price) - tax_withheld_amount
```

This represents the cash value after tax if all shares are sold.

## File Format

### Naming Convention
```
batch_{batch_id}_{vesting_date}.json
```

Example: `batch_BATCH_A1B2C3D4_2026-03-15.json`

### Location
Saved in parent directory (same location as release_activities JSON files)

### Format
Prettified JSON with 2-space indentation for readability

## Approval URL

Format: `https://dummy.com/batches/{batch_id}/approve`

This URL would integrate with an approval workflow system in production.

## Critical Rules

### Prerequisite Validation
- **MUST** call `calculate_tax_with_filters` before batch creation
- **MUST** have tax_results in state for vesting_date
- If missing → Clear error: "Call calculate_tax_with_filters first"

### Filter Traceability
- If filters applied → Include filter_summary in metadata
- If no filters → filter_summary is null
- Always set filter_applied boolean flag

### Unique Identification
- Every batch gets globally unique batch_id
- Format: BATCH_{8-char hex}
- Never reuse batch IDs

### Timestamp Format
- ISO 8601 format with UTC timezone
- Format: YYYY-MM-DDTHH:MM:SSZ
- Always use UTC (Z suffix)

## State Management

### Storage Location
`state["batches"][batch_id]`

### Structure
```python
{
  "metadata": {...},
  "records": [...]
}
```

### Persistence
- Remains in state for session duration
- Can be retrieved by batch_id
- Used for batch listing/management

## Integration with Workflow

### Typical Sequence
1. Fetch vesting details
2. (Optional) Extract and apply filters
3. Calculate tax → Creates tax_results
4. **Create batch** → Reads tax_results, creates batch
5. Present batch_id and approval_url to user

### Error Handling

#### Missing Tax Results
```python
{
  "status": "error",
  "message": "Error: Tax results not found for 2026-03-15. Call calculate_tax_with_filters first."
}
```

#### File Write Failure
- Batch still created in state
- Error logged but doesn't fail batch creation
- User notified of file save issue

## User Communication

### What to Show
- ✅ batch_id
- ✅ Record count
- ✅ Total shares released
- ✅ Total tax withheld
- ✅ Approval URL
- ✅ File path (if saved)

### What to Hide
- ❌ Internal state structure
- ❌ token_id references
- ❌ plan_id references

### Example User Message
```
✅ Batch created successfully!

Batch ID: BATCH_A1B2C3D4
Records: 25 employees
Total Shares: 125,000
Total Tax Withheld: $437,500.00
Filter Applied: Grant type is RSU AND Department is Engineering

Approval URL: https://dummy.com/batches/BATCH_A1B2C3D4/approve
Saved to: batch_BATCH_A1B2C3D4_2026-03-15.json
```

## Future Enhancements

- Batch status transitions (draft → pending → approved → executed)
- Batch approval/rejection tracking
- Batch editing capabilities
- Batch cancellation
- Audit trail for batch changes
