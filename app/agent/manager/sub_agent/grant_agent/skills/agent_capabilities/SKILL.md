---
name: grant-agent-capabilities
description: >
  Grant agent handles all questions about equity grants, plans,
  grant types, unvested shares, vesting schedules, performance
  conditions, grant status, and grant-participant relationships.
  Uses ADK artifacts for session-persistent data storage.
  Load once per session, read from artifact on all subsequent queries.
---

## Capabilities
1. Grant summary — type, status, plan breakdown
2. Natural language analysis via PandasAI
3. Specific grant lookup by grant_id
4. Cross-agent filtering by employee_ids for orchestrator

## Does NOT handle
- Vesting release workflow -> vesting_agent
- Participant compliance (KYC, address) -> participant_agent
- Release batches -> vesting_agent

## Artifact Keys
- grants_data.json -> full grant dataset (session-persistent)
- grant_query_result.json -> latest query result
- grant_detail_{grant_id}.json -> specific grant detail
