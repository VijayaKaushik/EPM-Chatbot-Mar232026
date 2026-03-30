---
name: client-ops-search
description: >
  Search client-specific documentation for operational questions.
  Covers CRM contacts, EPM contacts, escalation SLAs, how-to
  procedures, terminated employee policy, compliance notes.
  Client determined by client_id from session state.
---

# Client Ops Search Skill

## Workflow
[1] build_client_index() → ensure client artifact exists
[2] search_client_docs(query) → semantic search + answer
[3] Present answer with source and next action

## Topics Covered (from client documentation)
- CRM contacts and escalation contacts
- EPM team contacts and working hours
- Escalation SLAs (Critical/High/Medium)
- How to change address
- How to change email
- Terminated employee handling
- KYC compliance requirements
- Audit and data privacy notes

## Example Questions
- "Who is the CRM contact for this client?"
- "What is the escalation SLA for critical issues?"
- "How does this client handle terminated employees?"
- "What are the compliance requirements?"
- "How do I change a participant's address?"
- "Who is the EPM lead?"
- "What CRM system does this client use?"
- "What happens to unvested grants when employee is terminated?"
- "How long does address change take to process?"

## Response Format
- ANSWER: from documentation only
- SOURCE: document and section
- NEXT ACTION: specific step or N/A

## Client Isolation Rule
NEVER mix documents from different clients.
Always use client_id from session state to determine which
docs folder and artifact key to use.
