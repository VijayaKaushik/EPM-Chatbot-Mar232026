# 📚 End-to-End Architecture Summary

## The System in 60 Seconds

```
┌─ User: "Show vesting dates for May 2026" ─────────────────────┐
│                          (Browser)                              │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTP POST
┌────────────────────────────┴─────────────────────────────────┐
│ API Layer (/app/api/)                                         │
│ → Receives request                                             │
│ → Creates ChatRequest object                                   │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────┐
│ Service Layer (/app/service/)                                │
│ → Validates request                                            │
│ → Calls runner                                                 │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────┐
│ Manager Agent (/app/agent/manager/)                           │
│ → Analyzes: "This is vesting question"                        │
│ → Routes to: vesting_agent                                     │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────┐
│ Vesting Agent (/app/agent/.../vesting_agent/)                │
│ → Reads skill: vesting_schedule/SKILL.md                     │
│ → Decides to call: get_vesting_dates()                        │
│ → Calls: get_vesting_dates(month=5, year=2026)               │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────┐
│ Tool Function (tool.py)                                        │
│ → Loads: vesting_data/vesting_dates.csv                       │
│ → Filters: month=5, year=2026                                 │
│ → Finds: ["2026-05-15", "2026-05-20", "2026-05-25"]          │
│ → Returns: {status: success, vesting_dates: [...]}            │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────┐
│ Agent Formatting                                               │
│ → Takes tool output                                            │
│ → Creates: "Found 3 vesting dates in May 2026..."            │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────┐
│ Service Layer (Response Path)                                 │
│ → Formats as Server-Sent Events (SSE)                        │
│ → Streams response to user                                    │
└────────────────────────────┬─────────────────────────────────┘
                             │ Streaming Response
┌────────────────────────────┴─────────────────────────────────┐
│ User Sees Result in Browser                                   │
│ "Found 3 vesting dates in May 2026:                          │
│  - May 15, 2026                                               │
│  - May 20, 2026                                               │
│  - May 25, 2026"                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Folder Responsibilities Map

| 📁 Folder | 🎯 Role | 💼 Main Job |
|-----------|---------|-----------|
| `/api/` | Entry Point | Accept HTTP requests |
| `/service/` | Processor | Prepare requests for AI |
| `/agent/manager/` | Router | Route to specialists |
| `/agent/.../vesting_agent/` | Specialist | Handle vesting questions |
| `/models/` | Data Shapes | Define data structures |
| `/db/` | Database Access | Read/write to database |

---

## Key Learning Concepts

### 1. **Layered Architecture**
Each layer has ONE job:
- **API**: Accept requests ✓
- **Service**: Prepare data ✓
- **Agent**: Make decisions ✓
- **Data**: Store/retrieve ✓

### 2. **Agent & Tools**
- **Agent** = Brain (makes decisions)
- **Tool** = Worker (does actual work)
- Agent calls tools based on skills

### 3. **Skills**
- Guide agent behavior
- Say "when user asks X, use tool Y"
- Define workflows

### 4. **Sessions**
- Remember conversation context
- Store chat history
- Allow multi-turn conversations

### 5. **Data Files**
- `.csv` → Vesting data
- `.db` → Chat history
- Simple storage, easy to understand

---

## Quick File Guide

### If You Want to Understand...

**How requests flow:**
→ Read `/app/main.py` → `/app/api/chat.py` → `/app/service/chat_service.py`

**How agents work:**
→ Read `/app/agent/manager/agent.py` → `/app/agent/.../vesting_agent/agent.py`

**How tools work:**
→ Read `/app/agent/.../vesting_agent/tool.py`

**How data is stored:**
→ Look at `/app/agent/.../vesting_agent/vesting_data/`

**How sessions work:**
→ Read `/app/service/ai_workflow/runner_service.py`

**How responses are sent:**
→ Read `/app/service/chat_service.py` (exec_chat_sse function)

---

## Learning Checklist

After reading the guides, you should be able to:

- [ ] Explain what each folder does
- [ ] Draw the request flow from user to agent to tool
- [ ] Explain what a tool does
- [ ] Explain what a skill does
- [ ] Point to where vesting dates are stored
- [ ] Find where chat history is saved
- [ ] Understand how agent decides which tool to call
- [ ] Explain why system is organized in layers
- [ ] Find and read actual code for each layer
- [ ] Predict what happens when user asks a question

---

## 🎓 Next Steps

1. **Read the guides** (90 minutes total)
2. **Trace a request** in actual code (30 minutes)
3. **Add a new tool** to vesting_agent (60 minutes)
4. **Understand Google ADK** deeper (self-study)
5. **Contribute to the codebase** (make changes confidently)

---

## The Golden Rule

**Don't just read - TRACE!**

When learning a new system:
1. Find the entry point (main.py)
2. Click on imports to follow the flow
3. Read function signatures
4. Understand inputs/outputs
5. Repeat at each layer

This way you learn by **doing** not just reading.

---

## You're Ready!

You now have:
- ✅ Complete understanding of architecture
- ✅ Visual diagrams showing flows
- ✅ Real code examples to study
- ✅ Learning exercises to try
- ✅ Roadmap for deeper learning

**Time to code! 🚀**

Start with one guide, spend 30 minutes, then ask yourself:
> "Can I explain this to someone else?"

If yes → You're learning! If no → Re-read and trace the code.

Good luck! 🎉
