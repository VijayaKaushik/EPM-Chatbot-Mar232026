# Vesting Data Files

## Overview

The vesting data is organized into two main files and a subfolder:

- `vesting_dates.csv` - Stores vesting dates for all clients (loaded by `VestingDateService`)
- `vesting_details/` - Subfolder containing individual vesting date CSVs with participant details
- `README.md` - This documentation file

**Current Date**: March 25, 2026

## Folder Structure

```
vesting_data/
├── vesting_dates.csv          # Client vesting calendars
├── vesting_details/           # Individual vesting date details
│   ├── 2026-05-15.csv        # Participant data for May 15, 2026
│   ├── 2026-05-20.csv        # Participant data for May 20, 2026
│   ├── 2026-05-25.csv        # Participant data for May 25, 2026
│   ├── 2026-06-15.csv        # Participant data for June 15, 2026
│   ├── 2026-06-20.csv        # Participant data for June 20, 2026
│   ├── 2026-09-15.csv        # Participant data for September 15, 2026
│   ├── 2026-12-15.csv        # Participant data for December 15, 2026
│   ├── 2027-01-15.csv        # Participant data for January 15, 2027
│   ├── 2027-03-20.csv        # Participant data for March 20, 2027
│   └── 2027-06-18.csv        # Participant data for June 18, 2027
└── README.md                  # This file
```

## File Descriptions

### vesting_dates.csv
Stores vesting dates for all clients and is loaded dynamically by `VestingDateService` in `tool.py`.

**Columns**:
- `client_id` (string): Client identifier (e.g., "CLIENT_001")
- `vesting_date` (string): Vesting date in YYYY-MM-DD format

**Example**:
```csv
client_id,vesting_date
CLIENT_001,2026-05-15
CLIENT_001,2026-06-15
CLIENT_002,2026-04-10
```

### vesting_details/*.csv
Individual CSV files containing participant details for each vesting date. These are loaded by functions like `get_vesting_details`, `filter_participants`, etc.

**Columns**: 25+ columns including employee_id, employee_name, grant_type, shares_released, etc. (see VESTING_FIELDS in tool.py)

**Naming**: Files are named with the vesting date in YYYY-MM-DD format (e.g., `2026-05-15.csv`)

## Sample Data

### CLIENT_001 (10 vesting dates)
- 2026-05-15 (52 days from today) - 10 participants
- 2026-05-20 (57 days) - 12 participants
- 2026-05-25 (62 days) - 13 participants
- 2026-06-15 (83 days) - 11 participants
- 2026-06-20 (88 days) - 10 participants
- 2026-09-15 (174 days) - 12 participants
- 2026-12-15 (265 days) - 13 participants
- 2027-01-15 (296 days) - 11 participants
- 2027-03-20 (390 days) - 10 participants
- 2027-06-18 (480 days) - 12 participants

### CLIENT_002 (6 vesting dates)
- 2026-04-10 (16 days from today) - 11 participants
- 2026-05-10 (46 days) - 10 participants
- 2026-07-10 (107 days) - 13 participants
- 2026-08-10 (138 days) - 12 participants
- 2026-10-10 (199 days) - 11 participants
- 2027-02-15 (322 days) - 10 participants

## Query Examples

All queries return the standard response format:
```json
{
  "status": "success",
  "vesting_dates": ["2026-05-15", "2026-06-15", "2026-09-15"],
  "client_id": "CLIENT_001",
  "filter_type": "next_3",
  "total_found": 3,
  "message": "Retrieved 3 vesting date(s) for CLIENT_001 (next_3)"
}
```

### Query Patterns

| Intent | Parameters | Example |
|--------|-----------|---------|
| All dates | (none) | `get_vesting_dates(client_id="CLIENT_001")` |
| Next N dates | `count=3` | `get_vesting_dates(client_id="CLIENT_001", count=3)` |
| By month | `month=6, year=2026` | `get_vesting_dates(client_id="CLIENT_001", month=6, year=2026)` |
| Date range | `start_date="..."` | `get_vesting_dates(client_id="CLIENT_001", start_date="2026-06-01", end_date="2026-12-31")` |

### User Prompts

- "Give me next vesting date" → `count=1`
- "Show me next 3 vesting dates" → `count=3`
- "What are vesting dates in June?" → `month=6`
- "Get vesting dates for May 2027" → `month=5, year=2027`
- "List vesting dates from May to December 2026" → `start_date="2026-05-01", end_date="2026-12-31"`
- "Get all vesting dates" → (no filters)

## Adding More Data

### Add New Vesting Dates

1. **Add to vesting_dates.csv**:
```csv
CLIENT_001,2026-07-15
CLIENT_002,2026-07-15
```

2. **Create participant CSV** in `vesting_details/`:
   - File: `vesting_details/2026-07-15.csv`
   - Use same column structure as existing files
   - Include 10-15 participant rows with realistic data

### Add New Clients

1. **Add rows to vesting_dates.csv** with new client_id
2. **Create participant CSVs** for each of their vesting dates
3. **Update default client_id** in `get_vesting_dates()` if needed

## Future API Integration

To replace CSV with a real API:

1. **Vesting dates**: Update `VestingDateService._load_csv()` to call API
2. **Participant details**: Update `get_vesting_details()` to call API endpoint
3. **Keep same data structure** for compatibility

## Notes

- Dates are automatically sorted by `get_all_dates()`
- "Next N" filtering uses `datetime.now().date()` — in tests with fixed "today", consider mocking
- All filtering is **in-memory** — no database queries
- CSV files are cached after first load — app restart required to pick up changes during development
- Participant CSVs contain 25+ columns with employee, grant, and financial data
