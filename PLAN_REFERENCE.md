# 🎮 Vibe Coder → Production AI Engineer (Hard Mode): 16-Week Plan

> **Status:** Active - Phase 1 in progress
>
> **Last Updated:** March 26, 2026
>
> **Mission:** Strip away framework magic, build production-grade AI systems from first principles, and grow into a Senior Agentic AI Engineer
>
> **Active Project:** BookWorm (Weeks 1-4)
>
> **Companion Plan:** [Web3 Dev → Agentic AI Engineer](WEB3DEV_PLAN_REFERENCE.md)

---

# 📌 Daily Dashboard

| Date | Current Week | Current Phase | Active Project |
| --- | --- | --- | --- |
| Thu, March 26, 2026 | Week 2 | Phase 1 - The No Magic Zone | BookWorm |

## Today's Focus

| Icon | Task | Status |
| --- | --- | --- |
| 🧪 | Finish Week 2 streaming fundamentals: SSE flow, partial chunks, and streamed tool-call assembly | 🔄 In Progress |
| 📚 | Read `Building Applications with AI Agents` Ch 3 and `Clean Architecture` Ch 15 + 17 before Week 3 architecture decisions | 🔄 In Progress |
| 🤝 | Sync BookWorm backend boundaries with the companion web3 plan before memory work starts | ⚪ Not Started |

## Tomorrow / Up Next

- Week 3: multi-turn memory, token counting, and manual context truncation
- BookWorm architecture sync: define backend state boundaries before retrieval work starts
- Prepare Week 4 retrieval foundation: pgvector, BM25, and Reciprocal Rank Fusion

## Recently Completed

- `week_01_raw_api_combat/` missions added to the repo
- `week_02_stream_catcher/` missions added to the repo
- Shared BookWorm reference now aligned across both developer plans

---

# ⚔️ The Quest

> **Class:** Data Engineer → Production AI Engineer
>
> **Experience:** 6+ years in Data Engineering · Neo4j experience at Join Analytics · hands-on LangGraph and Claude Code experimentation
>
> **Party:** 2-person co-op (you + the web3 developer)
>
> **Final Boss:** Build an Autonomous Data Analyst Agent that safely queries a real database, self-corrects, and produces trustworthy reports

## Character Sheet

| Stat | Level | Strength | Gap to Close |
| --- | --- | --- | --- |
| Data Engineering | Senior | Pipelines, modeling, operational thinking | Translate data rigor into agent runtime discipline |
| Retrieval Systems | Mid-Senior | Neo4j, document pipelines, search intuition | Hybrid retrieval tuning, reranking, eval-driven iteration |
| LLM Mechanics | Mid | LangGraph experimentation, vibe coding speed | Raw provider APIs, streaming internals, tool-call state machines |
| Production AI | Mid | Strong backend instincts | Contracts, observability, adversarial testing, safe rollout habits |

*Pattern: strong infrastructure and data instincts, with the biggest upside coming from replacing "SDK intuition" with implementation-level understanding.*

## Phase Overview

| Phase | Weeks | Focus | Boss Fight | Status |
| --- | --- | --- | --- | --- |
| Phase 1 - The No Magic Zone | 1-3 | Raw APIs · Streaming · State management | Terminal multi-provider chat app with streaming and tool execution, built with zero AI frameworks | 🟢 Active |
| Phase 2 - Advanced Data RAG & GraphRAG | 4-7 | Hybrid retrieval · Reranking · Neo4j GraphRAG · pipeline automation | Automated ingestion pipeline that updates both Neo4j and a vector database from source documents | ⚫ Locked |
| Phase 3 - Production Agents & The Eval Crucible | 8-11 | Strict schemas · routing · evals · tracing | CI pipeline that runs evals on every PR and fails below quality threshold | ⚫ Locked |
| Phase 4 - The MCP Architect | 12-16 | MCP · database tools · cost routing · portfolio proof | Autonomous Data Analyst Agent connected to a real database with safe SQL generation and self-correction | ⚫ Locked |

---

# 📚 BookWorm Sync (Weeks 1-4)

> 🛠️ **Project:** BookWorm - agentic RAG knowledge companion
>
> 🔗 **Full Spec:** [BookWorm - Project Spec](https://www.notion.so/BookWorm-Project-Spec-26124426cd428123a182c3344120d79c?pvs=21)
>
> 🤝 **Shared Rule:** You do not merge your own PR. Each developer reviews the other's code and must be able to explain it before merge.
>
> 🏆 **Shared Boss Fight:** Multi-turn cited conversations where BookWorm can answer with grounded references such as chapter, page, or source section

BookWorm is the shared proving ground for Weeks 1-4 only. After Week 4, it becomes portfolio evidence and a reference implementation, while later phases broaden into standalone retrieval, agent, and MCP systems.

## How Weeks 1-4 Map Into BookWorm

| Week | Bruno Ownership | Why It Matters to BookWorm |
| --- | --- | --- |
| Week 1 | Raw provider client, JSON tool schemas, manual tool loop foundations | Gives BookWorm a backend that is debuggable without hiding behind SDK abstractions |
| Week 2 | FastAPI SSE and streaming backend | Powers real-time BookWorm responses for admin surfaces and future chat interfaces |
| Week 3 | Conversation memory, token budgeting, context truncation | Makes BookWorm multi-turn and prevents context blowups in longer sessions |
| Week 4 | Retrieval foundation with pgvector, BM25, and RRF | Establishes the first real search layer that the shared product can build on |

## Cross-Pollination Protocol

- You review the web3 developer's PRs; the web3 developer reviews yours
- The reviewer must be able to explain the implementation clearly in a short call before merge
- Shared architecture decisions happen before large retrieval or agent refactors
- BookWorm stays aligned on product goals, but each developer owns their implementation lane

## Shared Stack Split

- **You (Python):** raw provider adapters, streaming backend, ingestion, embeddings pipeline, memory logic, eval harness, retrieval backends
- **Web3 developer (TypeScript):** LangGraph orchestration, admin dashboard, Telegram integration, retrieval UX, frontend observability surfaces

---

# 🛡️ Phase 1 - The No Magic Zone (Weeks 1-3)

> **Mission:** Break dependence on LangChain and provider SDKs. If you cannot build it raw, you cannot debug it in production.

## Week 1 - Raw API Combat

- Write Python scripts using only `httpx` to call OpenAI and Anthropic-style chat APIs
- Hand-write raw JSON Schema tool definitions without Pydantic
- Manually handle tool-use response loops: detect tool call, execute mock function, send result back, continue until final answer
- Capture response anatomy, provider differences, retries, and failure handling notes
- BookWorm hook: this becomes the provider adapter layer for the shared project

**Read:** `AI Engineering` Ch 1, Ch 2 (skim), Ch 3 · `Building Applications with AI Agents` Ch 4 · `Clean Architecture` Ch 10-11

## Week 2 - The Stream Catcher

- Build a FastAPI backend that streams LLM responses with Server-Sent Events
- Parse raw SSE events and handle `[DONE]` boundaries cleanly
- Accumulate partial JSON fragments from streamed tool calls until the arguments are valid
- Expose a stable streaming surface that BookWorm can later plug into
- Treat this as interview-grade practice: streaming tool-call assembly is the hard part, not the easy token drip

**Read:** `Building Applications with AI Agents` Ch 3 · `Clean Architecture` Ch 15, Ch 17 · `AI Engineering` Ch 10 (light)

## Week 3 - State Management (Hard Way)

- Build multi-turn memory without `ConversationBufferMemory`
- Implement manual context-window truncation and token counting with `tiktoken`
- Decide what belongs in short-term memory, what belongs in retrieval, and what should be dropped
- Define the conversation-state contract BookWorm needs before hybrid retrieval begins
- Compare naive transcript growth vs budgeted memory windows

**Read:** `Building Applications with AI Agents` Ch 6 · `AI Engineering` Ch 6 (preview) · `Clean Architecture` Ch 20

### 👾 Phase 1 Mini-Boss

Build a terminal-based, multi-provider chat app with streaming and tool execution using zero AI frameworks. The outcome should prove that you understand the mechanics before moving back up to higher-level abstractions.

---

# 🕸️ Phase 2 - Advanced Data RAG & GraphRAG (Weeks 4-7)

> **Mission:** Turn core data-engineering strength into retrieval systems that behave like production software, not toy demos.

## Week 4 - Hybrid Search Engine

- Set up `pgvector`
- Implement BM25 keyword search plus vector similarity search
- Merge the result sets with Reciprocal Rank Fusion
- Add metadata filtering by book, chapter, and source type
- BookWorm hook: Week 4 is the last explicitly shared project week, and it establishes the first retrieval engine the product can trust

**Read:** `AI Engineering` Ch 5 (deep) · `Building Applications with AI Agents` Ch 6 · `Clean Architecture` Ch 15

## Week 5 - The Reranker Stage

- Add a cross-encoder reranker
- Use the production pattern: retrieve wide (`top 20`) then rerank narrow (`top 5`)
- Compare hybrid-only retrieval against hybrid-plus-reranker on a small evaluation set
- Document latency vs quality tradeoffs so you learn when reranking is worth the cost

**Read:** `AI Engineering` Ch 5 (deep re-read) · `Building Applications with AI Agents` Ch 6 · `Clean Architecture` Ch 17

## Week 6 - GraphRAG Ascension

- Use an LLM to extract entities and relationships from raw text
- Load them into Neo4j
- Combine vector retrieval with graph traversal for questions that require structure, not just semantic similarity
- Design retrieval flows such as: find the policy document, then find all employees who signed it

**Read:** `AI Engineering` Ch 5 (deep) · `Building Applications with AI Agents` Ch 6 · `Clean Architecture` Ch 22

## Week 7 - Pipeline Automation

- Wrap the ingestion-to-embedding flow in Airflow or Prefect
- Make the pipeline idempotent and observable enough to rerun safely
- Automate document ingestion, chunking, embedding, graph updates, and vector updates
- Treat orchestration as a system-design exercise, not just task scheduling

**Read:** `AI Engineering` Ch 5 (deep) · `Building Applications with AI Agents` Ch 6 · `Clean Architecture` Ch 15, Ch 17, Ch 22

### 👾 Phase 2 Mini-Boss

Ship an automated data pipeline that ingests PDFs, chunks them semantically, updates a Neo4j knowledge graph, and updates a vector database without manual babysitting.

---

# ⚖️ Phase 3 - Production Agents & The Eval Crucible (Weeks 8-11)

> **Mission:** Replace eye-test vibe coding with quantitative quality gates, explicit contracts, and runtime visibility.

## Week 8 - Strict Contracts & Defenses

- Refactor tools to use strict Pydantic v2 schemas
- Build adversarial tests that attempt prompt injection, unsafe actions, and sensitive-data leakage
- Add deterministic fallback logic for bad tool outputs and unsafe requests
- Force tool contracts to behave like production interfaces, not vibes

**Read:** `AI Engineering` Ch 4 (deep), Ch 6 · `Building Applications with AI Agents` Ch 4 · `Clean Architecture` Ch 20

## Week 9 - Advanced LangGraph Routing

- Build an error-correction DAG that retries broken SQL generation up to three times
- Feed runtime errors back into the graph so the agent can repair its own query
- Add human-in-the-loop interruption points for destructive database actions
- Compare state-machine routing to simpler linear tool loops

**Read:** `AI Engineering` Ch 6 · `Building Applications with AI Agents` Ch 5 · `Clean Architecture` Ch 19, Ch 20

## Week 10 - The Eval Crucible

- Build a golden dataset of 50 complex questions with expected SQL or expected answers
- Run `Ragas` or `TruLens` for faithfulness and answer-relevance scoring
- Track regressions over time instead of relying on ad hoc demos
- Learn to change prompts, retrieval, and tools based on measured failures

**Read:** `AI Engineering` Ch 4 (deep re-read) · `Building Applications with AI Agents` Ch 9-10 · `Clean Architecture` Ch 21

## Week 11 - Telemetry & Tracing

- Integrate Langfuse or Arize Phoenix tracing
- Capture graph steps, token usage, latency, and failure hotspots
- Build the habit of debugging with traces rather than intuition
- Define the minimum operational view you need before trusting an agent in production

**Read:** `AI Engineering` Ch 10 · `Building Applications with AI Agents` Ch 5, Ch 9-10 · `Clean Architecture` Ch 22

### 👾 Phase 3 Mini-Boss

Set up a CI/CD GitHub Action that runs the eval dataset on every PR. If the agent scores below 85% on the agreed quality bar, the pipeline fails.

---

# 🔌 Phase 4 - The MCP Architect (Weeks 12-16)

> **Mission:** Connect agents to real systems, control cost, and package the work into credible senior-level evidence.

## Week 12 - Model Context Protocol Server Setup

- Build a local Python MCP server using the official SDK
- Define clear tool boundaries before exposing anything sensitive
- Treat MCP as an interface contract, not just another wrapper
- Test local developer ergonomics early so tool definitions stay usable

**Read:** `Building Applications with AI Agents` Ch 2, Ch 5 · `AI Engineering` Ch 9 · `Clean Architecture` Ch 17, Ch 20

## Week 13 - The DB Bridge

- Expose PostgreSQL or BigQuery securely as MCP tools
- Restrict capabilities to safe, reviewable operations
- Test the tools natively in Claude Desktop or Cursor
- Document the difference between safe read access, dangerous writes, and human approval boundaries

**Read:** `Building Applications with AI Agents` Ch 5, Ch 8 · `AI Engineering` Ch 9-10 · `Clean Architecture` Ch 20-22

## Week 14 - Cost & Routing Optimization

- Implement semantic caching with Redis so repeated questions do not always hit the LLM
- Add model routing: cheap model for classification, stronger model for generation and harder reasoning
- Measure cost, latency, and quality before and after routing
- Learn to optimize without hiding failure cases

**Read:** `Building Applications with AI Agents` Ch 2, Ch 5, Ch 8 · `AI Engineering` Ch 9-10 · `Clean Architecture` Ch 17, Ch 21-22

## Week 15 - Portfolio Polish

- Rewrite CV bullets for Vertik and Data Providerz with hard metrics
- Turn the strongest projects into tight case studies with architecture, eval, latency, and cost evidence
- Draft the technical blog post on building GraphRAG with Neo4j and LangGraph
- Package the story so hiring teams can see engineering rigor, not just experimentation

**Read:** `AI Engineering` Ch 4, Ch 6, Ch 10 (re-read) · `Clean Architecture` Ch 21-22

## Week 16 - Job Hunt & Final Boss

- Publish or finalize the technical blog post
- Complete the Autonomous Data Analyst Agent
- Use that project as the anchor for applications, interviews, and portfolio walkthroughs
- Target AI-native roles with proof points: eval scores, safe SQL, tracing, and cost control

**Read:** `AI Engineering` Ch 4, Ch 6, Ch 10 (re-read) · `Clean Architecture` Ch 21-22

### 👾 Final Boss

Build the Autonomous Data Analyst Agent: an MCP server connected to a real database that takes natural-language questions, writes safe SQL, fixes its own syntax errors with LangGraph, and produces data reports you would actually trust.

---

# 📖 Reading Stack

> Week-level `Read:` lines are the primary source of truth during execution. The tables below are the map, but the weekly roadmap is the actual study contract.

## Must-Read Chapters

| Book | Role in the Plan | Must-Read Chapters |
| --- | --- | --- |
| `AI Engineering` | LLM application foundations, retrieval, evals, agents, production feedback loops | Ch 1, Ch 3, Ch 5 (deep), Ch 4 (deep later), Ch 6, Ch 9, Ch 10 |
| `Building Applications with AI Agents` | Tool use, orchestration, memory, scaling, evaluation | Ch 2, Ch 3, Ch 4, Ch 5 (deep), Ch 6, Ch 8, Ch 9-10 |
| `Clean Architecture` | Boundaries, dependency direction, use-case separation, production structure | Ch 10-11, Ch 15, Ch 17, Ch 19-22 |

## Chapter-to-Phase Map

| Phase | `AI Engineering` | `Building Applications with AI Agents` | `Clean Architecture` |
| --- | --- | --- | --- |
| Phase 1 (Weeks 1-3) | Ch 1, Ch 2 skim, Ch 3, Ch 6 preview, Ch 10 light | Ch 3, Ch 4, Ch 6 | Ch 10-11, Ch 15, Ch 17, Ch 20 |
| Phase 2 (Weeks 4-7) | Ch 5 deep | Ch 6 | Ch 15, Ch 17, Ch 22 |
| Phase 3 (Weeks 8-11) | Ch 4 deep, Ch 6, Ch 10 | Ch 4, Ch 5, Ch 9-10 | Ch 19-22 |
| Phase 4 (Weeks 12-16) | Ch 9-10, plus Ch 4 and Ch 6 re-reads in portfolio weeks | Ch 2, Ch 5, Ch 8 | Ch 17, Ch 20-22 |

## Suggested Read Order

1. `AI Engineering` Ch 1 → Ch 3 → Ch 5 → Ch 4 → Ch 6 → Ch 9 → Ch 10
2. `Building Applications with AI Agents` Ch 4 → Ch 3 → Ch 5 → Ch 6 → Ch 8 → Ch 9-10
3. `Clean Architecture` Ch 10-11 → Ch 15 → Ch 17 → Ch 20 → Ch 19 → Ch 21-22

---

# Weekly Checkpoint Template

```md
## Week [N] Checkpoint

### What I Built
- 

### What I Learned
- 

### What Broke or Surprised Me
- 

### Metrics
- Retrieval: Recall@5 = ?, MRR = ?
- Quality: Faithfulness = ? / Relevance = ?
- Cost: $/query = ?
- Latency: P50 = ?ms, P95 = ?ms

### Theory Used
- 

### Next Week
- 
```

---

# 🤝 Pairing Guidance

> You are still the engineer. AI is the pair who helps you think deeper, review harder, and move faster without stealing the reps.

## Session Modes

- **Architecture Review:** before building, ask what assumptions are weak, what boundaries are missing, and what failure modes you have not designed for
- **Explain First:** when a concept feels fuzzy, ask for explanation before implementation so you still write the code yourself
- **Code Review:** after building, request bug-risk review, missing tests, and architectural feedback
- **Unstuck:** if you have been stuck for 15+ minutes, describe what you tried and ask for a nudge instead of a full solution
- **Quiz Me:** after each major week or mini-boss, test whether the theory actually stuck

## Ground Rules

- Try first, then ask for help
- When you ask for help, include what you attempted and where the confusion starts
- Paste your code for review instead of outsourcing the implementation
- Use AI to compress feedback loops, not to skip the learning loop
- If a framework hides something important, rebuild the smaller version yourself once

## Review Standard for This Repo

- If a change touches BookWorm, both plans should still agree on the shared goal and ownership split
- If a change introduces new abstractions, explain what problem they solve and what lower-level mechanic they hide
- If a change cannot be measured, add the metric you would use to judge it later
