---
name: grant-analysis
description: >
  Analyze equity grant data using natural language queries.
  Covers grant type breakdown, unvested shares, plan distribution,
  performance conditions, grant status, expiring grants,
  officer grants, and employee grant counts.
  Always loads data into artifact first, then queries artifact.
---

## Workflow
[1] load_grants() -> load into artifact, get summary
[2] query_grants(query) -> PandasAI on artifact data
[3] Present results as table or summary

## Example Queries
- Which grant type has maximum unvested shares?
- How many active RSU grants are there?
- Which plan has the most participants?
- Show grants expiring in next 90 days
- Average grant value by grant type
- Which employees have more than 2 grants?
- Show performance condition grants
- Breakdown of grants by status
- Which grant type has highest percentage vested?

## Artifact Rule
- load_grants saves to grants_data.json on first call
- All subsequent queries read from artifact only
- source field in response confirms: disk or artifact
