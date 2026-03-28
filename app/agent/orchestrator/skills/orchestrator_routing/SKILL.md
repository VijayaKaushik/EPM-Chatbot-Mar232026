---
name: orchestrator-routing
description: >
  Routes equity management queries to the correct specialist agent.
  Handles vesting releases, participant compliance lookups, and
  cross-agent queries. Maintains conversation context across turns.
  Always calls route_query first, then delegates to correct agent.
---

# Orchestrator Routing Skill

## Decision Flow
[1] call route_query(query) -> get routing plan
[2] Act on plan:
    context_only  -> answer from session context, no agent call
    vesting_agent -> delegate full query to vesting_agent
    participant_agent -> delegate to participant_agent
    both -> vesting_agent first -> extract ids -> participant_agent
[3] call update_context after every agent completion
[4] Present result to user

## Agent Boundaries

vesting_agent owns:
  All release workflows, vesting data analysis,
  participant data within release context
  Runs its workflow end to end — do not interrupt

participant_agent owns:
  KYC, insider, blackout, address, W8/W9, ACH,
  account info — compliance and profile fields only

## Cross-Agent Rule
  Always: vesting_agent first -> employee_ids -> participant_agent
  Never: pass full records between agents
  Join: set intersection on employee_id keys only

## Context Reuse Rule
  Before calling any agent check route_query result
  If route = context_only -> use session data directly
  This avoids redundant agent calls
