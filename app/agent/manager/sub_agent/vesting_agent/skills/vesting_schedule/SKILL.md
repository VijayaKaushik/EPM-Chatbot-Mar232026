---
name: vesting-schedule
description: >
  View upcoming equity vesting dates and retrieve participant details
  for a specific vesting date. Use for informational queries only —
  not for release processing. Covers RSU, PSU, and Stock Option grants.
---

# Vesting Schedule Skill

## When to Use
Informational queries only — viewing dates and participant summaries.
For release processing, batch creation, or tax calculation → use release-workflow skill.

## Workflow
[1] get_vesting_dates(count) → show upcoming dates
[2] get_vesting_details(vesting_date) → show participant summary

## Stage 1: Get Vesting Dates
Tool: get_vesting_dates(count=1)
- Show dates in a clean list
- Ask which date to view details for

## Stage 2: Get Vesting Details
Tool: get_vesting_details(vesting_date, tool_context)
- Present participant table: employee, grant type, shares, net value, status
- Show total count and summary
- Never expose token_id to user