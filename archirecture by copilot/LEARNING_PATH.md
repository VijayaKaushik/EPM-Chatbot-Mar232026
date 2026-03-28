# Learning Path - Start Here

## 📚 You Now Have 3 Comprehensive Guides

I've created three documents to help you learn this system:

### 1. **ARCHITECTURE_GUIDE.md** 📖
**Best for**: Understanding the BIG PICTURE

What you'll learn:
- What each folder does
- How user request flows through system
- Complete end-to-end journey
- Session management concepts
- Layered architecture pattern

**Start here if you want to**: Understand the overall system design

---

### 2. **ARCHITECTURE_DIAGRAMS.md** 🎨
**Best for**: VISUAL learners

What you'll learn:
- System architecture diagram
- Data flow visualization
- Folder responsibilities diagram
- Request processing pipeline
- Memory/session flow

**Start here if you want to**: See how things connect visually

---

### 3. **VESTING_AGENT_GUIDE.md** 🔧
**Best for**: DEEP DIVE into actual code

What you'll learn:
- How vesting_agent works step-by-step
- Actual code examples
- Code patterns to understand
- Learning exercises to try
- Common questions answered

**Start here if you want to**: Understand real code with examples

---

## 🎯 Recommended Learning Path

### Week 1: Understand Architecture
- [ ] Read ARCHITECTURE_GUIDE.md (30 mins)
- [ ] Look at ARCHITECTURE_DIAGRAMS.md (20 mins)
- [ ] Open folders in IDE and match to guide

### Week 2: Learn About Vesting Agent
- [ ] Read VESTING_AGENT_GUIDE.md (45 mins)
- [ ] Look at actual files:
  - [ ] `/app/agent/manager/sub_agent/vesting_agent/agent.py`
  - [ ] `/app/agent/manager/sub_agent/vesting_agent/tool.py`
  - [ ] `/app/agent/manager/sub_agent/vesting_agent/skills/vesting_schedule/SKILL.md`

### Week 3: Trace a Request
- [ ] Start with `/app/main.py`
- [ ] Follow to `/app/api/chat.py`
- [ ] Follow to `/app/service/chat_service.py`
- [ ] Follow to `/app/service/ai_workflow/runner_service.py`
- [ ] Follow to `/app/agent/manager/agent.py`
- [ ] Follow to `/app/agent/manager/sub_agent/vesting_agent/agent.py`

### Week 4: Experiment
- [ ] Try adding a new tool to vesting_agent
- [ ] Try modifying a tool response
- [ ] Try changing a skill workflow

---

## 🗂️ Quick Reference: What Each Folder Does

```
📁 /app/api/              → User sends request here (HTTP endpoints)
📁 /app/service/          → Process request, call agents
📁 /app/agent/manager/    → Smart router agent
📁 /app/agent/.../sub_agent/vesting_agent/  → Specialist for vesting
📁 /app/models/           → Data structure definitions
📁 /app/db/               → Database access code
```

---

## 🔍 Key Concepts to Understand

### 1. **Layered Architecture**
```
Request comes in
    ↓ (API adds structure)
Service processes it
    ↓ (Runner sets up)
Agent decides
    ↓ (Specialist executes)
Tool does work
    ↓ (Service formats)
Response goes out
```

### 2. **Agents and Tools**
- **Agent** = Decision maker (uses AI)
- **Tool** = Worker function (does actual work)
- Agent decides which tool to call
- Tool returns result
- Agent formats for user

### 3. **Skills**
- SKILL.md files guide agent behavior
- They say "when user says X, use tool Y"
- They define workflows

### 4. **Data Files**
- `.csv` files store vesting data
- `.db` files store chat history
- Service layer reads from these

### 5. **Session Management**
- Each conversation has a session_id
- Runner stores history in database
- Agent can see previous messages
- Creates context for smarter responses

---

## 💡 Pro Tips for Learning Code

### Tip 1: Trace, Don't Read
Don't just read files sequentially. Instead:
1. Start at `/main.py`
2. See it imports from `/api/`
3. Click on that import
4. See what it does
5. Click on its imports
6. Continue until you reach the bottom

### Tip 2: Print Debug Statements
Add `print()` everywhere:
```python
def my_function(param):
    print(f"Function called with: {param}")
    result = do_something(param)
    print(f"Function returning: {result}")
    return result
```

### Tip 3: Read Docstrings First
Every function should have a docstring:
```python
def get_vesting_dates(...) -> Dict:
    """
    WHAT IT DOES
    WHEN AGENT CALLS IT
    WHAT IT RETURNS
    """
```

### Tip 4: Find the Data
If you want to understand code, find the data it works with:
- Vesting agent uses: `/vesting_data/vesting_dates.csv`
- Chat service uses: `my_agent_data.db`

### Tip 5: Map Dependencies
Make a simple map:
```
main.py
  → api/chat.py
    → service/chat_service.py
      → ai_workflow/runner_service.py
        → agent/manager/agent.py
          → sub_agent/vesting_agent/agent.py
            → tool.py
              → vesting_data/
```

---

## 🧪 Learning Exercises

### Exercise 1: The Silent Trace (30 mins)
- Don't run code yet
- Just read `/app/main.py` → `/app/api/chat.py` → `/app/service/chat_service.py`
- Write down the function calls in order
- Then trace it in your head

### Exercise 2: Print the Journey (30 mins)
1. Add `print("STEP X")` statements at each layer
2. Send a test message to the API
3. Watch the prints in order
4. See the request flow

### Exercise 3: Change the Response (30 mins)
1. Find `get_vesting_dates()` in tool.py
2. Change the returned message format
3. Test with API
4. See how your change appears to user

### Exercise 4: Add a New Tool (60 mins)
1. Create new function in tool.py: `get_employee_count()`
2. Register in agent.py
3. Call it through API
4. See the new tool work

### Exercise 5: Understand CSV Loading (30 mins)
1. Open `/vesting_data/vesting_dates.csv`
2. Open `tool.py` and find VestingDateService
3. Understand how it reads CSV
4. Print CSV contents to see what data looks like

---

## 🎓 After You Learn the Basics

Once comfortable with architecture:

### Deep Dive into Google ADK
- Understand `LlmAgent` class
- Learn how tools are registered
- Learn skill matching

### Database Concepts
- Understand SQLite basics
- Learn how sessions are stored
- Query chat history

### API Design
- Understand REST endpoints
- Learn request/response patterns
- Understand streaming (SSE)

### AI Concepts
- How LLMs make decisions
- What prompts do
- Function calling

---

## 🆘 When You Get Stuck

### "I don't understand this function"
1. Find its docstring
2. Find where it's called
3. Find what calls it
4. Look at inputs/outputs

### "I don't know what this variable is"
1. Search for where it's defined
2. Find its type
3. Look at what operations happen to it

### "I don't know what this file does"
1. Look at its imports
2. Look at its exports (functions/classes)
3. Find where it's imported
4. See how it's used

### "The data seems wrong"
1. Check the CSV/database files
2. Add print statements
3. Print actual vs expected
4. Find where discrepancy occurs

---

## 📊 The 30-Minute Mental Model

After reading these guides, you should understand:

1. **User sends message** → Goes to `/api/chat.py`
2. **API validates** → Sends to `/service/chat_service.py`
3. **Service prepares** → Calls `/ai_workflow/runner_service.py`
4. **Runner manages session** → Calls manager agent
5. **Manager agent routes** → Decides which specialist
6. **Specialist agent works** → Reads skills, calls tools
7. **Tool executes** → Loads data, processes, returns
8. **Agent formats** → Makes human-friendly response
9. **Service streams** → Sends back to user
10. **User sees answer** → In browser/app

That's the whole flow! Everything else is details.

---

## 🚀 Ready to Start?

1. **First time here**: Read ARCHITECTURE_GUIDE.md
2. **Want visuals**: Read ARCHITECTURE_DIAGRAMS.md
3. **Want code examples**: Read VESTING_AGENT_GUIDE.md
4. **Want to code**: Do the learning exercises

Pick one, spend 30 minutes, then ask yourself:
- "Can I explain this to someone else?"
- "Can I find the relevant code?"
- "Can I predict what happens when X occurs?"

If yes to all three → Move to next guide! 

Happy learning! 🎉
