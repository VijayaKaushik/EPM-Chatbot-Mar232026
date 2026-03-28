# 📚 Repository Learning Resources - INDEX

## Welcome! 🎓

This repository now has **comprehensive learning resources** to help you understand the entire system end-to-end.

---

## 🎯 Start Here Based on Your Style

### 👨‍💼 "I want the executive summary"
**Read:** `LEARNING_SUMMARY.md` (5 minutes)
- Quick overview
- One-page explanations
- Visual diagrams

### 🏃 "I'm in a hurry"
**Read:** `LEARNING_PATH.md` (10 minutes)
- Your learning roadmap
- Quick tips
- Pro learning strategies

### 📖 "I want complete understanding"
**Read:** `ARCHITECTURE_GUIDE.md` (45 minutes)
- Detailed explanations
- Each layer explained
- Code patterns

### 🎨 "I'm a visual learner"
**Read:** `ARCHITECTURE_DIAGRAMS.md` (30 minutes)
- System architecture diagram
- Data flow visualization
- Process pipelines
- Memory/session flows

### 🔧 "Show me the code!"
**Read:** `VESTING_AGENT_GUIDE.md` (60 minutes)
- Real code examples
- Step-by-step walkthroughs
- Learning exercises
- Code patterns

---

## 📋 Document Guide

### LEARNING_SUMMARY.md (5 min read)
**What**: Quick overview and checklist  
**Best for**: Getting oriented  
**Contains**: 60-second explanation, folder map, key concepts

### LEARNING_PATH.md (10 min read)
**What**: Your roadmap for learning  
**Best for**: Planning your learning journey  
**Contains**: Recommended path, tips, exercises, troubleshooting

### ARCHITECTURE_GUIDE.md (45 min read)
**What**: Complete system explanation  
**Best for**: Understanding the big picture  
**Contains**: Folder roles, request flow, layer patterns, concepts

### ARCHITECTURE_DIAGRAMS.md (30 min read)
**What**: Visual explanations  
**Best for**: Visual learners  
**Contains**: System diagrams, data flows, processes, memory patterns

### VESTING_AGENT_GUIDE.md (60 min read)
**What**: Deep dive with code  
**Best for**: Understanding real code  
**Contains**: Code examples, patterns, exercises, Q&A

### CLAUDE.md (Project Context)
**What**: Guidelines for working with this project  
**Best for**: Development reference  
**Contains**: Commands, architecture overview, conventions

---

## 🗂️ Repository Structure Explained

```
epm-chatbot/
│
├── 📖 LEARNING_SUMMARY.md          ← Start here! Quick overview
├── 📖 LEARNING_PATH.md              ← Your learning roadmap
├── 📖 ARCHITECTURE_GUIDE.md         ← Complete guide
├── 📖 ARCHITECTURE_DIAGRAMS.md      ← Visual flows
├── 📖 VESTING_AGENT_GUIDE.md        ← Code deep dive
│
├── app/                             # Application code
│   ├── main.py                      # Entry point
│   ├── api/                         # HTTP endpoints
│   ├── service/                     # Business logic
│   ├── agent/                       # AI agents
│   ├── models/                      # Data structures
│   └── db/                          # Database access
│
├── pyproject.toml                   # Dependencies
└── *.db files                       # Databases
```

---

## 🎓 Recommended Learning Path

### Week 1: Foundation (4 hours)
- [ ] Read `LEARNING_SUMMARY.md` (5 min)
- [ ] Read `LEARNING_PATH.md` (10 min)
- [ ] Read `ARCHITECTURE_GUIDE.md` (45 min)
- [ ] Look at actual `/app/` folders (2 hours)

### Week 2: Visual Understanding (2 hours)
- [ ] Read `ARCHITECTURE_DIAGRAMS.md` (30 min)
- [ ] Trace request in code from `/app/main.py` (1.5 hours)

### Week 3: Deep Code (3 hours)
- [ ] Read `VESTING_AGENT_GUIDE.md` (60 min)
- [ ] Study `/app/agent/.../vesting_agent/` code (1.5 hours)
- [ ] Try Exercise 1 from guide (30 min)

### Week 4: Experimentation (4 hours)
- [ ] Do learning exercises from guides (2 hours)
- [ ] Try modifying a tool (1 hour)
- [ ] Add a new tool (1 hour)

---

## 🔍 Quick Navigation

### "I want to understand how X works"

**User sends a message:**
→ Read: LEARNING_PATH.md + trace `/app/main.py`

**Agent makes a decision:**
→ Read: ARCHITECTURE_GUIDE.md (Part 3)

**Tool loads data:**
→ Read: VESTING_AGENT_GUIDE.md (Part 2)

**Response goes to user:**
→ Read: ARCHITECTURE_GUIDE.md (Part 2)

**Session remembers context:**
→ Read: ARCHITECTURE_GUIDE.md + ARCHITECTURE_DIAGRAMS.md

**Agent picks specialist:**
→ Read: VESTING_AGENT_GUIDE.md (Flow Example)

---

## 💡 Learning Tips

### Tip 1: Use This When Confused
1. Open `ARCHITECTURE_DIAGRAMS.md`
2. Find the relevant diagram
3. See the visual flow
4. Read `ARCHITECTURE_GUIDE.md` section
5. Look at actual code

### Tip 2: Trace, Don't Read
- Don't just read files sequentially
- Follow imports from `/app/main.py`
- Click on each import in IDE
- See how code connects

### Tip 3: Find the Data
- Vesting data: `/app/agent/.../vesting_agent/vesting_data/`
- Chat history: `my_agent_data.db`
- Understanding data = understanding code

### Tip 4: Add Print Statements
```python
def my_func(x):
    print(f"ENTERING: my_func with x={x}")
    result = do_something(x)
    print(f"EXITING: my_func returning {result}")
    return result
```
Then test and watch the console!

### Tip 5: One Layer at a Time
- First understand: API layer
- Then understand: Service layer
- Then understand: Agent layer
- Then understand: Tool layer
- Then understand: Data layer

---

## 🆘 If You Get Stuck

### "I don't understand this folder"
→ Read ARCHITECTURE_GUIDE.md, find the folder, read that section

### "I don't understand this file"
→ Read VESTING_AGENT_GUIDE.md (Code Patterns section)

### "I don't understand this function"
→ Read ARCHITECTURE_DIAGRAMS.md and find it in a diagram

### "I'm lost in the code"
→ Start from `/app/main.py` and trace forward

### "I want to code but don't know where"
→ Read VESTING_AGENT_GUIDE.md (Learning Exercises section)

---

## 📚 Beyond These Guides

Once you understand the basics:

1. **Google ADK Documentation**
   - Learn `LlmAgent` class deeply
   - Understand tool registration
   - Learn skill matching

2. **Python Concepts**
   - Decorators (@router.post)
   - Type hints (str, Dict, Optional)
   - Async/await (async def)

3. **FastAPI**
   - Routing
   - Request/Response models
   - Dependency injection

4. **Database**
   - SQLite basics
   - Session storage
   - Query patterns

5. **AI Concepts**
   - LLM prompting
   - Function calling
   - Token usage

---

## ✅ You'll Know You're Ready When...

- [ ] You can explain the 5 layers without reading notes
- [ ] You can point to code for each folder
- [ ] You can trace a user message to response
- [ ] You can add a new tool and test it
- [ ] You can modify a skill workflow
- [ ] You understand why each folder exists
- [ ] You could explain it to a colleague

---

## 🚀 Your Next Steps

1. **Pick a guide** from the list above
2. **Spend 30 minutes** reading it
3. **Ask yourself**: "Can I explain this to someone?"
4. **If yes**: Move to next guide
5. **If no**: Re-read and trace the code
6. **Once confident**: Try a learning exercise

---

## 📞 Need Help?

### If you're confused about...

**Architecture**: → ARCHITECTURE_GUIDE.md  
**Visuals**: → ARCHITECTURE_DIAGRAMS.md  
**Code**: → VESTING_AGENT_GUIDE.md  
**Learning**: → LEARNING_PATH.md  
**Overview**: → LEARNING_SUMMARY.md  

---

## 🎉 Final Thoughts

You now have **everything you need** to understand this system:

✅ Comprehensive guides  
✅ Visual diagrams  
✅ Code examples  
✅ Learning exercises  
✅ Troubleshooting tips  

**The rest is up to you!**

Start with 30 minutes of reading, then code. Learning happens by doing.

Good luck! 🚀

---

**Happy Learning!**

*Created: March 25, 2026*  
*For: Learning to Code*  
*Scope: End-to-End System Understanding*
