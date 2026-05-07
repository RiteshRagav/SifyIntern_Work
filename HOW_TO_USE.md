# AgentFlow AI — How to Use

**Live Application:** https://your-project.vercel.app

---

## What Is AgentFlow AI?

AgentFlow AI is an intelligent multi-agent system where **three specialized AI agents work together** to answer your queries — one plans, one executes, and one validates. Unlike a regular chatbot that gives you a single response, AgentFlow breaks complex tasks into structured steps and delivers high-quality, validated output.

Think of it like a professional team:
- 📋 **PreAct** = The Project Manager who plans the work
- ⚡ **ReAct** = The Specialist who executes the plan
- ✅ **ReFlect** = The Reviewer who checks the quality

---

## Getting Started

### Step 1 — Open the Application
Navigate to the live URL in any modern browser (Chrome, Firefox, Edge).

You will see the **AgentFlow AI** dashboard with:
- A **left sidebar** listing 7 domains to choose from
- A **top navigation bar** with three mode buttons
- A **chat area** in the center
- A **text input bar** at the bottom

---

## The Three Modes

### 💬 Normal Chat
A direct AI conversation — fast, simple, one response.

**Best for:** Quick questions, factual lookups, simple tasks.

**How to use:**
1. Click **"Normal Chat"** in the top-right
2. Type your question in the input bar
3. Press **"Send"** or hit Enter
4. Get an instant response

---

### 🤖 Multi-Agent (Recommended — Main Feature)
The full three-agent pipeline: PreAct plans → ReAct executes → ReFlect validates.

**Best for:** Complex tasks, detailed reports, structured content, professional documents.

**How to use:**
1. Click **"Multi-Agent"** in the top-right
2. *(Optional)* Select a domain from the left sidebar, or leave on **"Auto-Detect"**
3. Type your task in the input bar and press **"Send"**
4. **Wait for the Plan** — PreAct will generate a step-by-step execution plan
5. **Review the Plan** — Read through what the AI intends to do
6. **Click "Approve & Execute"** — ReAct begins executing each step
7. Watch the agents work in **real-time** as output streams to the screen
8. **ReFlect** reviews and scores the final output
9. Your complete, validated result appears

---

### ↔️ Compare Mode
Runs Normal Chat and Multi-Agent **side by side** with the same prompt simultaneously.

**Best for:** Seeing the quality difference between a direct response and the multi-agent pipeline.

**How to use:**
1. Click **"Compare"** in the top-right
2. Type your prompt and press Send
3. Left panel = Normal Chat response
4. Right panel = Multi-Agent pipeline output
5. Compare the depth, structure, and quality

---

## Choosing a Domain

The left sidebar lets you select a domain so the AI adapts its tone, structure, and expertise accordingly.

| Domain | Best For |
|--------|----------|
| **Auto-Detect** | Let the AI figure it out from your query |
| **Software** | Code design, APIs, architecture, technical docs |
| **Education** | Courses, lesson plans, training materials |
| **Healthcare** | Patient guides, medical summaries, health content |
| **Marketing** | Campaigns, strategies, copy, brand messaging |
| **Finance** | Investment analysis, financial reports, budgets |
| **Legal** | Contract summaries, policy drafts, compliance |
| **General** | Anything that doesn't fit the above |

> **Tip:** You can just use Auto-Detect for everything — the system detects the right domain automatically from your query.

---

## Sample Prompts to Try

Copy and paste any of these directly into the input bar.

### 🔵 Software
```
Design a REST API for a user authentication system with JWT tokens,
including all endpoints, request/response schemas, and security best practices.
```

### 🟢 Education
```
Create a 4-week beginner curriculum for learning Python programming,
including weekly topics, hands-on projects, and assessment strategies.
```

### 🔴 Healthcare
```
Write a patient guide explaining how to manage Type 2 Diabetes through
diet, exercise, and medication, in simple and clear language.
```

### 🟣 Marketing
```
Design a complete go-to-market strategy for an AI productivity app
targeting remote teams, including positioning, channels, and a 90-day launch plan.
```

### 🟡 Finance
```
Create an investment analysis framework for evaluating early-stage AI startups,
including financial metrics, risk assessment, and due diligence checklist.
```

### 🟠 Legal
```
Summarize the key clauses that should appear in a SaaS subscription agreement
covering data privacy, liability, termination rights, and IP ownership —
written in plain English for a non-lawyer founder.
```

### ⚪ General
```
Create a project management framework for a 6-month product development cycle
with a team of 8 people, covering planning, execution, and risk management.
```

---

## Understanding the Multi-Agent Workflow

When you submit a query in Multi-Agent mode, here is what happens step by step:

```
You type a query
        │
        ▼
┌───────────────────────────────────┐
│  STAGE 1: PreAct (Planner)        │
│                                   │
│  • Reads your query               │
│  • Detects the domain             │
│  • Breaks the task into steps     │
│  • Shows you the plan             │
└───────────────┬───────────────────┘
                │
        YOU REVIEW AND APPROVE
                │
                ▼
┌───────────────────────────────────┐
│  STAGE 2: ReAct (Executor)        │
│                                   │
│  • Follows the approved plan      │
│  • Works through each step        │
│  • Generates the actual content   │
│  • Streams output in real-time    │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  STAGE 3: ReFlect (Validator)     │
│                                   │
│  • Reviews the ReAct output       │
│  • Checks quality against plan    │
│  • Scores it (0–10)               │
│  • Refines if needed              │
└───────────────┬───────────────────┘
                │
                ▼
        ✅ Final Validated Output
```

---

## Tips for Best Results

1. **Be specific** — The more detail you give, the better the plan and output.
   - ❌ "Write a marketing plan"
   - ✅ "Write a digital marketing plan for a B2B SaaS tool targeting HR managers in mid-sized companies"

2. **Read the plan before approving** — PreAct's plan shows exactly what will be generated. If it looks wrong, start a new chat with a clearer prompt.

3. **Use Compare mode** to see the value — Side-by-side comparison makes the quality difference obvious.

4. **Try different domains** — The tone, structure, and content depth changes significantly between domains.

5. **Start a new chat** for each new topic — Click **"+ New Chat"** in the top-left to reset.

---

## Frequently Asked Questions

**Q: Why does it take longer than a regular chatbot?**
Three agents are running sequentially — each one reads, thinks, and writes. The extra time directly produces better, more structured output.

**Q: What is the "Approve & Execute" step?**
This is intentional. You review the AI's plan before it writes anything — giving you control over what will be generated. This is called Human-in-the-Loop design.

**Q: Can I use it without selecting a domain?**
Yes. "Auto-Detect" (top of the sidebar) lets the system figure out the right domain from your query automatically.

**Q: What if the response seems incomplete?**
Try the same prompt with more specific details. Alternatively, switch to a different domain manually if Auto-Detect picked the wrong one.

**Q: Is my data stored?**
Session data and chat history are stored in MongoDB for continuity within a session. No data is shared externally.

---

## Quick Reference

| Action | How |
|--------|-----|
| Start a new conversation | Click **"+ New Chat"** (top-left) |
| Change AI mode | Click **Normal Chat / Multi-Agent / Compare** (top-right) |
| Select a domain | Click any domain in the left sidebar |
| Submit a query | Type in input bar → press Enter or click **Send** |
| Approve agent plan | Click **"Approve & Execute"** when plan appears |
| Reset and try again | Click **"+ New Chat"** |

---

*Built with FastAPI · React · MongoDB · ChromaDB · Groq (Llama 3.3 70B)*
