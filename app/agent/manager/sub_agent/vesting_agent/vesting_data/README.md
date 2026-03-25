# Vesting Dates CSV

## Overview

The `vesting_dates.csv` file stores vesting dates for all clients and is loaded dynamically by `VestingDateService` in `tool.py`.

**Current Date**: March 25, 2026

## File Format

### Columns
- `client_id` (string): Client identifier (e.g., "CLIENT_001")
- `vesting_date` (string): Vesting date in YYYY-MM-DD format

### Example
```csv
client_id,vesting_date
CLIENT_001,2026-05-15
CLIENT_001,2026-06-15
CLIENT_002,2026-04-10
```

## Sample Data

### CLIENT_001 (7 upcoming dates)
- 2026-05-15 (52 days from today)
- 2026-06-15 (83 days)
- 2026-09-15 (174 days)
- 2026-12-15 (265 days)
- 2027-01-15 (296 days)
- 2027-03-20 (390 days)
- 2027-06-18 (480 days)

### CLIENT_002 (7 upcoming dates)
- 2026-04-10 (16 days from today)
- 2026-05-10 (46 days)
- 2026-07-10 (107 days)
- 2026-08-10 (138 days)
- 2026-10-10 (199 days)
- 2027-02-15 (322 days)

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
| All dates for client | (no filters) | `get_vesting_dates(client_id="CLIENT_001")` |
| Next N future dates | `count=N` | `get_vesting_dates(client_id="CLIENT_001", count=3)` |
| Dates in a month | `month=M, year=Y` | `get_vesting_dates(client_id="CLIENT_001", month=6, year=2026)` → June 2026 dates |
| Current month dates | `month=M` | `get_vesting_dates(client_id="CLIENT_001", month=3)` → March 2026 dates (empty in this case) |
| Date range | `start_date, end_date` | `get_vesting_dates(client_id="CLIENT_001", start_date="2026-06-01", end_date="2026-12-31")` |

### User Prompts

- **"Give me next vesting date"** → `count=1`
- **"Show me the next 3 vesting dates"** → `count=3`
- **"What are the vesting dates in June?"** → `month=6`
- **"List vesting dates for May 2027"** → `month=5, year=2027`
- **"Get all vesting dates"** → (no filters)
- **"Show vesting from May to December 2026"** → `start_date="2026-05-01", end_date="2026-12-31"`

## Adding More Clients

1. Open `vesting_dates.csv` in your editor or spreadsheet application
2. Add new rows with format: `CLIENT_XXX,YYYY-MM-DD`
3. Save the file
4. The service will automatically load new data on the next query

Example:
```csv
CLIENT_003,2026-04-15
CLIENT_003,2026-07-15
CLIENT_003,2027-01-15
```

## Adding More Dates for Existing Clients

Simply append new rows to the CSV. The `VestingDateService` will:
- Load all rows on first use
- Cache in memory
- Sort dates automatically
- Filter based on query parameters

## Future API Integration

To replace CSV with a real API:

1. Create an HTTP client in `VestingDateService`:
```python
def _load_csv(self) -> pd.DataFrame:
    response = requests.get("https://api.client.com/vesting-dates")
    data = response.json()
    return pd.DataFrame(data["vesting_dates"])
```

2. The rest of the filtering methods remain unchanged
3. All tool-level logic stays the same

## Notes

- Dates are automatically sorted by `get_all_dates()`
- "Next N" filtering uses `datetime.now().date()` — in tests with fixed "today", consider mocking `datetime`
- All filtering is **in-memory** — no database queries
- CSV is cached after first load — app restart required to pick up CSV changes during development

