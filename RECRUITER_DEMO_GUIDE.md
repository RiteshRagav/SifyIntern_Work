# 🤖 AgentFlow AI — Recruiter Demo Guide

> **Live URL:** `https://your-project.vercel.app`  
> **Backend API:** `https://agentflow-backend-58fq.onrender.com`  
> **GitHub:** `https://github.com/RiteshRagav/SifyIntern_Work`

---

## 🏗️ System Architecture (Say This First)

> *"AgentFlow AI is a dynamic multi-agent orchestration system. Instead of a single AI answering a question, three specialized agents collaborate — one plans, one executes, and one validates. This mirrors how professional teams work."*

```
User Query
    ↓
┌─────────────────────────────────────────────┐
│  PreAct Agent (PLANNER)                     │
│  - Analyses the query                       │
│  - Auto-detects domain (Software/Finance…)  │
│  - Breaks task into logical steps           │
│  - User reviews & approves the plan         │
└──────────────────┬──────────────────────────┘
                   ↓ (after approval)
┌─────────────────────────────────────────────┐
│  ReAct Agent (EXECUTOR)                     │
│  - Follows the PreAct plan step by step     │
│  - Reason → Act → Observe loop              │
│  - Generates actual content per domain      │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  ReFlect Agent (VALIDATOR)                  │
│  - Reviews ReAct's output against plan      │
│  - Scores quality (0–10)                    │
│  - Revises or approves final output         │
└──────────────────┬──────────────────────────┘
                   ↓
            ✅ Final Output
```

---

## 🖥️ Three UI Modes

| Mode | What it does | When to demo it |
|------|-------------|-----------------|
| **Normal Chat** | Direct LLM response (no agents) | Show speed |
| **Multi-Agent** | Full PreAct → ReAct → ReFlect pipeline | Main showcase |
| **Compare** | Both modes side-by-side simultaneously | Show difference |

---

## 🚀 Demo Sequence (Do This in Order)

### Demo 1 — Normal Chat Mode (30 seconds)
**Click:** `Normal Chat` button → type this prompt → hit Send:

```
What are the SOLID principles in software engineering?
```

**Say:**
> *"Normal Chat is a direct LLM call — fast, simple. But watch what Multi-Agent does with the same type of task."*

---

### Demo 2 — Multi-Agent Mode: Software Domain (Main Demo)
**Click:** `Multi-Agent` → Select domain `Software` → type:

```
Create a complete REST API design for a user authentication system with JWT tokens, including all endpoints, request/response schemas, error handling strategy, and security best practices.
```

**Walk through each step while it runs:**

1. **PreAct Planning Phase:**
   > *"The PreAct agent is now analyzing the query. It's detecting the domain as 'Software', breaking the task into steps, and generating a plan I can review before anything is executed."*

2. **Plan Review (Approval UI appears):**
   > *"This is the Human-in-the-Loop feature. I can see exactly what the AI plans to do — and I can approve, modify, or reject it before any content is generated. This is critical for enterprise use cases."*
   
   Click **"Approve & Execute"**

3. **ReAct Execution Phase:**
   > *"The ReAct agent follows a Reason → Act → Observe loop — it reasons about each step, performs the action, and observes the result before moving to the next. You can see it working in real-time via WebSocket streaming."*

4. **ReFlect Validation Phase:**
   > *"Finally, ReFlect reviews the output against the original plan, scores it for quality, and either approves it or revises it. This quality gate ensures consistent, high-quality responses."*

---

### Demo 3 — Multi-Agent Mode: Marketing Domain
**Click:** `+ New Chat` → `Multi-Agent` → Select `Marketing` → type:

```
Design a complete go-to-market strategy for an AI-powered productivity app targeting remote teams. Include positioning, target segments, messaging framework, channel strategy, and 90-day launch plan.
```

**Say:**
> *"Notice how the system automatically adapts — the plan structure, writing tone, and content format all change based on the Marketing domain. The same architecture serves completely different industries."*

---

### Demo 4 — Compare Mode (Most Impressive Visual)
**Click:** `Compare` → type:

```
Analyze the key trends shaping the future of artificial intelligence in healthcare over the next 5 years.
```

**Say:**
> *"Compare mode runs Normal Chat and Multi-Agent simultaneously. On the left you see a direct LLM response — fast but flat. On the right you see the multi-agent pipeline — structured, validated, and domain-aware. The quality difference is immediately visible."*

---

## 📋 Domain-Specific Test Prompts

### 💻 Software
```
Design a microservices architecture for an e-commerce platform with 
payment processing, inventory management, and order fulfillment services. 
Include service communication patterns, data consistency strategies, 
and deployment considerations.
```

```
Create a comprehensive code review checklist for a Python FastAPI backend 
covering security, performance, testing, and maintainability.
```

### 🎓 Education
```
Design a 4-week curriculum for teaching machine learning fundamentals 
to computer science undergraduates with no prior ML experience. 
Include learning objectives, weekly topics, hands-on projects, 
and assessment strategies.
```

```
Create an interactive lesson plan for explaining neural networks to 
high school students using real-world analogies and simple activities.
```

### 🏥 Healthcare
```
Create a patient education guide explaining Type 2 Diabetes management 
including diet, exercise, medication adherence, and monitoring strategies 
in clear, accessible language for newly diagnosed patients.
```

### 📣 Marketing
```
Develop a complete content marketing strategy for a B2B SaaS company 
entering the HR tech space. Include buyer personas, content pillars, 
SEO strategy, distribution channels, and 6-month content calendar.
```

```
Create a social media campaign for launching a sustainable fashion brand 
targeting Gen Z consumers, including platform strategy, content themes, 
influencer approach, and KPIs.
```

### 💰 Finance
```
Create a comprehensive investment analysis framework for evaluating 
early-stage AI startups, including financial metrics, market sizing 
methodology, risk assessment criteria, and due diligence checklist.
```

### ⚖️ Legal
```
Draft a clear summary of key clauses that should be included in a 
SaaS subscription agreement, covering data privacy, liability limits, 
termination rights, and IP ownership — written in plain English 
for a non-lawyer founder.
```

### 🌐 General (Auto-Detect)
```
Create a detailed project management framework for a 6-month product 
development cycle with a team of 8 people, covering planning, 
execution, risk management, and stakeholder communication.
```

---

## 🛠️ Technical Talking Points

### Tech Stack
> *"The backend is built on FastAPI with Python — async, high-performance. The frontend uses React with Vite for instant HMR. WebSocket handles real-time agent streaming. MongoDB persists sessions and chat history. ChromaDB provides RAG (Retrieval-Augmented Generation) for domain-specific knowledge injection."*

### Why Three Agents?
> *"Single LLM prompts hit a ceiling — they can't plan, execute, and validate simultaneously. The three-agent pattern is inspired by how human teams work: a PM plans, a developer builds, a QA engineer reviews. Each agent has a specialized system prompt and focus area."*

### Domain Detection
> *"The system doesn't just respond differently per domain — it automatically detects the domain from your query. Ask about blood pressure and it switches to Healthcare mode. Ask about contract clauses and it uses Legal domain guidelines. Zero configuration needed."*

### Real-time Streaming
> *"Every agent event streams to the frontend via WebSocket in real-time. You're not waiting for a final response — you see the AI thinking, step by step. This transparency is key for enterprise trust."*

### RAG Integration
> *"ChromaDB stores domain-specific knowledge that's injected into each agent's context. This means the agents have persistent, retrievable memory beyond the LLM's training data."*

---

## ❓ Recruiter Q&A Cheat Sheet

**Q: What LLM does this use?**
> "Groq's Llama 3.3 70B — a frontier open-source model running on Groq's custom inference hardware for ultra-low latency. The architecture is provider-agnostic though — it works with OpenAI, Gemini, or any OpenAI-compatible endpoint."

**Q: How is this different from just using ChatGPT?**
> "ChatGPT is one model in one turn. AgentFlow is a coordinated pipeline where three specialized agents with different roles collaborate. The plan-approve-execute-validate loop adds transparency and quality control that a single LLM can't provide."

**Q: What's the most complex part technically?**
> "The async SSE streaming pipeline — each agent emits events via Server-Sent Events while running concurrently, and the frontend subscribes to these events per session via WebSocket. Managing state across three agents without race conditions was the core challenge."

**Q: Does it use fine-tuning?**
> "No fine-tuning — the intelligence comes from three things: carefully engineered system prompts per agent, dynamic domain templates injected as context, and the orchestration logic that sequences the agents correctly. Prompt engineering and architecture over model training."

**Q: Can it scale?**
> "Yes — FastAPI is async by design, MongoDB handles horizontal scaling, and the stateless agent pipeline can be distributed. The current free-tier deployment is for demo purposes; production would use managed services."

---

## 📊 Key Metrics to Mention

| Metric | Value |
|--------|-------|
| Agent pipeline stages | 3 (PreAct → ReAct → ReFlect) |
| Supported domains | 7 + Auto-detect |
| Streaming protocol | WebSocket + SSE |
| Max agent iterations | 8 per query |
| LLM provider | Groq (Llama 3.3 70B) |
| DB | MongoDB + ChromaDB |
| Frontend framework | React + Vite |
| Backend framework | FastAPI (Python) |
| Deployment | Render (backend) + Vercel (frontend) |

---

## 🎯 One-Line Project Summary

> **"AgentFlow AI is a domain-aware, multi-agent orchestration system that replaces single-shot LLM prompts with a collaborative pipeline of specialized AI agents — enabling transparent, structured, and high-quality content generation across 7 professional domains."**
