---
name: agent-capabilities
description: >
  Describes the full capabilities of the Vesting Agent.
  Used by the orchestrator to understand what this agent handles —
  vesting schedules, release workflow, batch creation, tax calculation,
  and vesting data analysis.
---
```

Content should cover:
```
## What This Agent Does
Single source of truth for orchestrator routing decisions.

## Capabilities

### 1. Vesting Schedule
- Get upcoming vesting dates
- Get participant details for a vesting date
- Triggers: "show vesting dates", "vesting details for June 15"

### 2. Release Workflow (Path B)
- Filter participants by grant type, officer status, tax method
- Calculate tax with admin-provided FMV and sales price
- Create batch, update vesting file, generate approval URL
- Supports multiple batches per vesting date
- Triggers: "prepare release", "create batch", "calculate tax for release"

### 3. Data Analysis
- Natural language queries on vesting data across all dates
- Aggregation, filtering, grouping, trend analysis
- Triggers: "analyze vesting data", "how many RSU grants", "breakdown by department"

## What This Agent Does NOT Handle
- Simulate release (separate workflow — different agent/skill)
- Post-approval amendments (external workflow tool)
- Participant profile data (participant agent handles this)
- Document management (client document agent handles this)

## Required Context From Orchestrator
- vesting_date (if already known from user message)
- filter preferences (if stated by user)
- user intent classification