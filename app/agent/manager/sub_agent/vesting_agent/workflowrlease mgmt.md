Step 1: GET VESTING DATES
        get_vesting_dates()

Step 2: GET VESTING DETAILS  
        get_vesting_details(vesting_date)
        → Shows all unbatched participants

Step 3: FILTER / SCOPE (not a batch yet — just a selection)
        filter_participants(vesting_date, filters)
        → Filter by: grant_type, officer_status, tax_method
        → Returns filtered participant list for review
        → No IDs assigned yet — just a working selection

Step 4: CALCULATE TAX
        calculate_tax(vesting_date, fmv, sales_price, filters)
        → Tax calculated only for filtered participants
        → Returns tax summary per participant

Step 5: CREATE BATCH = PREPARE FOR APPROVAL
        create_batch(vesting_date, filters, fmv, sales_price)
        → This IS the approval preparation
        → Generates batch_id (UUID)
        → Updates vesting CSV: writes batch_id + tax columns
          into each matched participant row
        → Generates approval URL
        → Batched participants excluded from future batches
        → Returns: batch_id, approval_url, participant count,
                   tax summary


After Step 2 (get_vesting_details) the admin has two paths:

PATH A — SIMULATE (what-if, no side effects)
│
├── simulate_release(vesting_date, filters, fmv, sales_price)
│   → Applies filters (grant_type, officer_status, tax_method)
│   → Calculates tax for matched participants
│   → Returns preview: participant count, tax summary, 
│     per-participant breakdown
│   → NOTHING written to CSV
│   → NO batch_id created
│   → NO approval URL
│   → Admin can run multiple simulations with different
│     parameters before committing
│
└── Admin reviews simulation results, adjusts parameters,
    simulates again until satisfied

PATH B — ACTUAL RELEASE (commits to vesting file)
│
├── Step 3: filter_participants (scope selection)
├── Step 4: calculate_tax (with actual FMV/sales price)  
└── Step 5: create_batch
            → batch_id assigned
            → CSV updated with batch_id + tax columns
            → approval URL generated
