# Welcome & Intent Collection Skill

## Overview
Greet users and classify their intent to route to appropriate workflow.

## Node: welcome_node

**Purpose**: Entry point for user interaction

**Actions**:
1. Greet user (first-time or returning)
2. Analyze user message for intent
3. Classify intent:
   - "tax_calculation" → route to tax workflow
   - "release_management" → route to release workflow
   - unclear → show capabilities

**State Updates**:
- `user_intent`: Classified intent
- `workflow_stage`: Next stage to execute

## Intent Keywords

- **Tax Calculation**: "tax", "calculate", "vesting", "FMV", "sales"
- **Release Management**: "release", "schedule", "timeline"
- **Data Analysis**: "analyze", "report", "breakdown"

## Routing Logic

```python
if intent == "tax_calculation":
    workflow_stage = "vesting_dates"
else:
    workflow_stage = "welcome"  # Stay and ask for clarification
```
