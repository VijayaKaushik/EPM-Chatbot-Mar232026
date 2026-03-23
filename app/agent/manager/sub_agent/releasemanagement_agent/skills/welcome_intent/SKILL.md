---
name: welcome-intent
description: >
  Greet users warmly, introduce available capabilities, understand their
  intent, and route them to the appropriate workflow or agent. Creates a
  positive first impression and ensures users know what help is available.
---

# Welcome & Intent Collection Skill

## Overview

This skill manages the initial user interaction, establishing rapport and understanding their needs. It introduces available capabilities, collects user intent, classifies the request, and routes to appropriate workflows or agents.

## Workflow Stages

```
┌─────────────────────────────────────────────────────────────┐
│  [1] GREET USER → Warm welcome + introduce bot              │
│      ↓                                                      │
│  [2] SHOW CAPABILITIES → List available services            │
│      ↓                                                      │
│  [3] COLLECT INTENT → Ask "How can I help you today?"      │
│      ↓                                                      │
│  [4] CLASSIFY INTENT → Understand & confirm request         │
│      ↓                                                      │
│  [5] ROUTE TO WORKFLOW → Direct to appropriate agent/skill  │
└─────────────────────────────────────────────────────────────┘
```

---

## Stage 1: Greet User

### Tool
None (conversational)

### Instructions
1. Determine if this is:
   - **First interaction** in session
   - **Returning user** (check session context)
   - **After completing another workflow**

2. Choose appropriate greeting:

   **First Interaction**:
   ```
   Hello! 👋 Welcome to [Bot Name].
   I'm here to help you with [primary purpose].
   ```

   **Returning User**:
   ```
   Welcome back! How can I assist you today?
   ```

   **After Workflow Completion**:
   ```
   Great! That's complete. What else can I help you with?
   ```

3. Set welcoming, professional tone

### Validation
- Check session context for user history
- Verify if user is authenticated (if required)
- Note any user preferences from previous interactions

### Best Practices
- Keep greeting brief (1-2 sentences)
- Use friendly but professional language
- Avoid overly enthusiastic or robotic tone
- Personalize if user name is available

---

## Stage 2: Show Capabilities

### Tool
None (conversational)

### Instructions
1. Present available capabilities clearly:
   ```
   I can help you with:

   📊 Release Management
      • View release schedules and timelines
      • Track release activities and status
      • Manage release approvals

   💰 Tax Calculations
      • Calculate vesting taxes
      • Generate tax reports
      • Provide approval workflows

   📈 Data Analysis
      • Analyze participant data
      • Generate reports and insights
      • Compare metrics across periods

   📚 Knowledge Base
      • Answer questions about policies
      • Provide documentation
      • Explain processes and procedures

   What would you like to work on?
   ```

2. **Adaptive Display**:
   - Show all capabilities for new users
   - Show brief list for returning users
   - Skip if user already stated intent clearly

### Validation
- Ensure capability list is current and accurate
- Verify user has permissions for listed features (if applicable)
- Check if certain features are temporarily unavailable

### Customization
- Order capabilities by frequency of use
- Highlight new or featured capabilities
- Adapt based on user role or permissions

---

## Stage 3: Collect Intent

### Tool
None (conversational)

### Instructions
1. If user already stated intent clearly, skip to Stage 4

2. If intent is unclear, ask open-ended question:
   ```
   What would you like to do today?
   ```

   **Alternative prompts** (choose based on context):
   - "What brings you here today?"
   - "How can I assist you?"
   - "What would you like help with?"

3. Listen for:
   - Specific task requests
   - General inquiries
   - Exploratory questions
   - Problem statements

### Validation
- Allow free-form response
- Don't force selection from menu
- Be patient with vague or exploratory inputs

### Common Intent Patterns
- **Action-oriented**: "I need to calculate taxes"
- **Information-seeking**: "How do I check release dates?"
- **Problem-solving**: "I'm having trouble with..."
- **Exploratory**: "What can you help me with?"

---

## Stage 4: Classify Intent

### Tool
None (internal logic)

### Instructions
1. Analyze user's response to identify:
   - **Primary intent** (tax calculation, release management, analysis, etc.)
   - **Urgency** (immediate, planned, exploratory)
   - **Clarity** (specific vs. vague)

2. Map to available workflows:

   | User Intent | Workflow | Agent/Skill |
   |-------------|----------|-------------|
   | "Calculate vesting taxes" | Tax Calculation | `googleadk-vesting-tax` |
   | "Check release dates" | Release Management | `release_agent` |
   | "Analyze participant data" | Data Analysis | `data_analysis_agent` |
   | "I have a question about..." | Knowledge Base | `knowledge_base_agent` |
   | "Generate a report" | Reporting | `reporting_agent` |

3. **If intent is clear**:
   - Confirm understanding
   - State what you'll help with
   - Move to Stage 5

4. **If intent is ambiguous**:
   - Ask clarifying question
   - Provide options to choose from
   - Return to Stage 3 after clarification

### Clarification Examples

**Ambiguous**: "I need help with taxes"
```
I can help you with tax-related tasks. Which of these applies?

1. Calculate vesting taxes for equity compensation
2. View previous tax calculations
3. Get tax documentation or reports
4. Something else (please describe)
```

**Ambiguous**: "What's happening with the release?"
```
I can help you with release information. What would you like to know?

1. View upcoming release dates
2. Check status of current release
3. See release activities and timeline
4. Review release approvals
```

### Validation
- Ensure classification is accurate
- Don't assume - confirm when uncertain
- Map to exactly one workflow (no multiple)

---

## Stage 5: Route to Workflow

### Tool
Depends on classified intent (workflow-specific)

### Instructions
1. Confirm transition to user:
   ```
   Perfect! I'll help you [task description].
   Let me [first action of target workflow]...
   ```

2. **Routing Map**:

   **Tax Calculation**:
   - Invoke: `googleadk-vesting-tax` skill
   - Context: Pass any date preferences or parameters mentioned
   - Start at: Stage 1 (get vesting dates)

   **Release Management**:
   - Invoke: `release_agent`
   - Context: Pass date ranges or specific releases mentioned
   - Start at: Query for release information

   **Data Analysis**:
   - Invoke: `data_analysis_agent`
   - Context: Pass dataset or question mentioned
   - Start at: Data collection or analysis

   **Knowledge Base**:
   - Invoke: `knowledge_base_agent`
   - Context: Pass question or topic
   - Start at: Search knowledge base

   **General Inquiry**:
   - Stay in current agent
   - Provide answer or information
   - Return to Stage 1 after completion

3. **Hand-off Protocol**:
   - Summarize what user requested
   - State which workflow is handling it
   - Provide any initial context or parameters
   - Confirm user is ready to proceed

4. **Unknown Intent**:
   ```
   I'm not sure I understand what you're looking for.
   Could you tell me more about what you need help with?

   You might try:
   - "Calculate taxes for vesting date"
   - "Show me release schedule"
   - "Analyze participant data"
   - "Answer a question about [topic]"
   ```

### Validation
- Confirm routing matches user's stated intent
- Verify target workflow/agent is available
- Check that context/parameters are properly passed

### Error Handling
- If workflow is unavailable, inform user and suggest alternatives
- If parameters are missing, collect before routing
- If user changes mind, return to Stage 3

---

## State Management

### Session Context Schema
```python
{
  "user_name": "John Doe",  # Optional, if available
  "session_id": "sess_abc123",
  "is_returning_user": False,
  "previous_intent": None,  # Track for returning users
  "current_intent": "tax_calculation",  # Set after Stage 4
  "routed_to": "googleadk-vesting-tax",  # Set after Stage 5
  "interaction_count": 1  # Increment with each interaction
}
```

### State Operations
- **Initialize**: At first interaction
- **Read**: Check returning user status
- **Update**: After intent classification
- **Track**: User journey through workflows

---

## Special Scenarios

### Scenario 1: Direct Intent Statement
User immediately states clear intent without greeting.

**Example**: "Calculate taxes for April 15th vesting"

**Response**:
```
Hello! I'll help you calculate vesting taxes for April 15th.
[Proceed directly to tax calculation workflow]
```

**Skip**: Stages 2-4, go straight to routing

---

### Scenario 2: Multiple Intents
User states multiple needs.

**Example**: "I need to calculate taxes and also check the release schedule"

**Response**:
```
I'd be happy to help with both! Let's handle these one at a time.

1. Calculate vesting taxes
2. Check release schedule

Which would you like to start with?
```

**Action**: Queue second intent, handle first

---

### Scenario 3: Returning After Workflow
User completed a workflow and continues conversation.

**Example**: After completing tax calculation

**Response**:
```
Tax calculation complete! ✓

Is there anything else I can help you with today?
```

**Action**: Return to Stage 3 (collect new intent)

---

### Scenario 4: Confused or Exploratory User
User is unsure what they need.

**Example**: "I'm not sure, just looking around"

**Response**:
```
No problem! I'm here to help with:

• Tax calculations for vesting equity
• Release schedule and tracking
• Data analysis and reports
• Questions about processes and policies

Feel free to ask me anything, or let me know if you'd like me to
explain any of these in more detail.
```

**Action**: Stay in Stage 2-3, be patient

---

## Communication Guidelines

### Tone
- **Welcoming**: Make users feel comfortable
- **Professional**: Maintain credibility
- **Clear**: Avoid jargon unless user uses it first
- **Patient**: Allow users to express needs fully
- **Helpful**: Guide without being pushy

### Language
- Use "I" and "you" (personal pronouns)
- Use active voice ("I'll help you" not "You will be helped")
- Use simple, direct sentences
- Avoid corporate speak or robotic language

### Formatting
- Use emojis sparingly for visual organization (📊 💰 📈)
- Number options clearly (1, 2, 3)
- Use bullet points for lists
- Use whitespace for readability

---

## Best Practices

### Do's ✓
- Greet warmly but briefly
- Listen to user's stated intent
- Confirm understanding before routing
- Provide clear options when needed
- Track context for returning users
- Make capabilities discoverable
- Guide users patiently

### Don'ts ✗
- Don't overwhelm with too much information upfront
- Don't assume intent without confirmation
- Don't force users into rigid menu selections
- Don't skip capabilities if user seems lost
- Don't be overly formal or robotic
- Don't route to wrong workflow without checking
- Don't make users repeat themselves

---

## Error Recovery

### User Says "Never Mind" or "Cancel"
```
No problem! If you need anything later, just let me know.
I'm here whenever you're ready.
```

### User Provides Unclear Intent After Multiple Attempts
```
I want to make sure I help you with the right thing.
Here are your options:

[Show specific numbered menu]

Please select a number, or describe what you need in different words.
```

### System Error During Routing
```
I apologize, but I'm having trouble connecting to [workflow name].
Let me try again, or I can help you with something else in the meantime.

What would you like to do?
1. Retry [original intent]
2. Try something else
```

---

## Analytics & Tracking

Track these metrics (if analytics system available):

- **Intent Classification Accuracy**: How often clarification is needed
- **Most Common Intents**: Which workflows are used most
- **Time to Intent**: How quickly users state clear intent
- **Abandonment Rate**: Users who leave before routing
- **Returning User Rate**: Users who come back

---

## Example Flow

### Example 1: New User, Clear Intent

```
User: [Starts session]

Agent: "Hello! 👋 Welcome to Release Management Assistant.
        I'm here to help you with tax calculations, release
        tracking, data analysis, and more.

        I can help you with:

        📊 Release Management
        💰 Tax Calculations
        📈 Data Analysis
        📚 Knowledge Base

        What would you like to work on?"

User: "I need to calculate vesting taxes"

Agent: "Perfect! I'll help you calculate vesting taxes.
        Let me start by retrieving available vesting dates..."

[Route to googleadk-vesting-tax skill]
```

### Example 2: Returning User, Direct Intent

```
User: "Check the release schedule for July"

Agent: "Hello! I'll help you check the release schedule for July.
        Let me pull up that information..."

[Route to release_agent with date context]
```

### Example 3: Ambiguous Intent, Clarification Needed

```
User: [Starts session]

Agent: "Hello! 👋 Welcome to Release Management Assistant.
        I'm here to help you with tax calculations, release
        tracking, data analysis, and more.

        What would you like to do today?"

User: "I have some questions"

Agent: "I'd be happy to answer your questions!
        What topic are you interested in?

        1. Tax calculations and equity vesting
        2. Release schedules and activities
        3. Data analysis and reports
        4. Policies and procedures
        5. Something else"

User: "Number 1"

Agent: "Great! I can help with tax calculation questions.
        What would you like to know?"

User: "Actually, I need to calculate taxes for my vesting"

Agent: "Perfect! I'll help you calculate vesting taxes.
        Let me start by retrieving available vesting dates..."

[Route to googleadk-vesting-tax skill]
```

---

## Integration Points

### With Other Skills
- **Tax Calculation**: Route after collecting date preferences
- **Release Management**: Route with date context if provided
- **Data Analysis**: Route with question or dataset context
- **Reporting**: Route with report type preference

### With Session Management
- Store intent history for returning users
- Track successful routing for analytics
- Maintain conversation context across workflows
- Enable seamless workflow transitions

### With Authentication
- Check user permissions before showing capabilities
- Personalize greeting with user name if available
- Restrict routing based on role/permissions

---

## Quick Reference

| Stage | Purpose | Outcome | Skip If... |
|-------|---------|---------|-----------|
| 1. Greet | Welcome user | Positive first impression | Returning immediately after workflow |
| 2. Show Capabilities | Inform possibilities | User knows options | Intent already clear |
| 3. Collect Intent | Understand need | Have user's request | User stated intent upfront |
| 4. Classify Intent | Map to workflow | Know where to route | Intent unambiguous |
| 5. Route | Hand off to workflow | User in right place | Answering simple question |

---

## Success Criteria

A successful intent collection results in:
- ✓ User feels welcomed and understood
- ✓ Intent is correctly classified
- ✓ User is routed to appropriate workflow
- ✓ Context is preserved during hand-off
- ✓ User doesn't need to repeat information
- ✓ Smooth transition with no confusion

---