---
name: guide-search
description: >
  Search official user guide documentation to answer application
  how-to questions. Covers participant guide and release vesting guide.
  Returns answer with source section and next action suggestion.
---

# Guide Search Skill

## Workflow
[1] build_index() -> ensure FAISS index artifact exists
[2] search_guides(query) -> semantic search + answer synthesis
[3] Present answer with source and next action

## Topics Covered

### Release & Vesting Guide
- Release simulation steps
- Vesting date selection
- Validation checks
- Approval workflow
- Best practices

### Participant & Grant Guide
- Login and access
- Dashboard navigation
- Viewing grants
- Tracking vesting
- Viewing releases
- Updating profile
- Completing KYC

## Response Format
Always structure response as:
- Answer: clear explanation from documentation
- Source: document and section
- Next Action: specific step to take in the app

## Example Questions
- "How do I simulate a release?"
- "What is KYC and how do I complete it?"
- "How do I view my vesting schedule?"
- "What does the dashboard show?"
- "How do I update my profile?"
- "What are the steps to approve a release?"
- "How do I track vesting dates?"
- "What is a grant?"
- "What should I do if a participant is blocked?"
- "How do I view release history?"
