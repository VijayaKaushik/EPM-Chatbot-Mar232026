---
name: planning-skill
description: >
  Create execution plans before workflow execution to ensure proper
  step sequencing and validation.
---

# Planning Skill

## Purpose

Creates structured execution plans before running vesting release workflows. Ensures:
- Proper tool call sequencing
- Prerequisite validation
- Clear workflow visibility for users
- Detection of filters vs parameters

## Workflow

1. **Analyze user query** for intent and requirements
2. **Detect filters** (grant_type, shares, department, etc.)
3. **Detect parameters** (FMV, sales price)
4. **Create step-by-step plan** with proper dependencies
5. **Present plan** to user for confirmation
6. **Execute steps** in strict sequence

## Plan Structure

Each plan contains:
- **plan_id**: Unique identifier
- **vesting_date**: Target vesting date
- **steps**: Ordered list of actions
- **has_filters**: Boolean flag
- **fmv_value**: Detected FMV parameter (if any)
- **sales_value**: Detected sales parameter (if any)

## Execution Rules

1. **Always create plan first** - Never skip planning phase
2. **Never skip steps** - Execute in exact order
3. **Validate prerequisites** - Check state before each step
4. **Handle errors gracefully** - Provide clear next-step guidance
5. **Show plan to user** - Get confirmation before execution

## Example Plans

### Basic workflow (no filters):
1. Fetch vesting details
2. Calculate tax (with FMV/sales)
3. Create batch

### Filtered workflow:
1. Fetch vesting details
2. Extract filters from query
3. Apply filters to data
4. Calculate tax (with FMV/sales)
5. Create batch

## Critical Distinctions

**FILTERS** (subset data):
- grant_type = "RSU"
- shares_released > 10000
- department = "Engineering"

**PARAMETERS** (simulation inputs):
- FMV = 10.0
- sales = 12.0

The plan must correctly identify which is which to build the right sequence.
