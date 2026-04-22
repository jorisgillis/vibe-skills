---
name: architect
description: Use this skill when the user or coding agent provides a plan or idea for a software product and asks for architectural guidance. This skill will define a software architecture, propose a domain model, break the work into dependency-ordered epics, and assess whether the coding agent can start working. Use it any time someone describes a product idea and wants to know how to build it or where to start.
---

# Architect Skill

Help the user go from a product idea to a clear architectural plan and an ordered list of epics a coding agent can act on.

## Default to Simple

Your job is to design something that works well for 1–1000 users, not for the hypothetical future where the product has millions. Premature scalability creates complexity that slows a team down and is almost never needed at the start.

Practical defaults — reach for these unless there's a specific reason not to:
- **Backend**: Express (not Fastify, Hapi, etc.) — it's the most widely known and documented Node.js framework. Don't choose a faster framework unless the user has said performance is a concern.
- **Real-time**: SSE (Server-Sent Events) for server→client push. A simple POST endpoint for client→server. Don't reach for WebSockets unless you genuinely need low-latency bidirectional communication (e.g. a collaborative editor, live cursor tracking).
- **No extra infrastructure** unless the requirements demand it: no Redis, no message queues, no caching layers. These add operational burden and complexity. A standard database handles a lot more than people think.
- **PostgreSQL** for relational data, **S3-compatible storage** for files. Avoid exotic databases unless the data model clearly doesn't fit a relational model.

If a choice deviates from these defaults, the justification should be grounded in something the user actually said, not in theoretical future scale.

## Output Structure

Produce these four sections in order:

### 1. Architecture Overview

Choose a concrete technology stack. Don't hedge with "you could use X or Y" — pick one. Include:
- Frontend, backend, database, auth approach
- Any notable infrastructure choices (only what the problem actually requires)
- 1-2 sentences of reasoning per choice — grounded in the specific problem, not generic praise

### 2. Domain Model

Identify the core domain objects (entities) and their relationships. This makes it concrete what's being built before any code is written. A simple list is fine:

```
User — has many Tasks
Task — belongs to User, has many Tags, may belong to a Project
Project — has many Tasks, belongs to User
Tag — has many Tasks (many-to-many)
```

Include key attributes where they clarify something non-obvious. The goal is alignment on what the system is, not a complete data dictionary.

### 3. Epics Breakdown

List the epics in **dependency order** — each epic should be completable (or at least startable) using only what came before it. A useful heuristic: if Epic B needs something from Epic A to function or be tested, A comes first.

Typical ordering:
1. Data layer / backend scaffolding (database schema, models, migrations)
2. Core API endpoints (enough to support the first user-facing feature)
3. Authentication (usually depends on the data layer and API being in place)
4. Core domain features (the main thing the product does)
5. UI / frontend (depends on the API being testable)
6. Supporting features (notifications, search, analytics, etc.)

Don't include deployment or CI/CD as epics — these are operational concerns, not things a coding agent needs to tackle to build the product.

For each epic, write 2-4 bullet points describing what it involves. Keep them concrete enough that a coding agent knows what to implement, not so detailed that they pre-empt design decisions.

### 4. Feasibility Assessment

Answer: can the coding agent start now, or is more research needed?

- If yes: say so directly and point to Epic 1 as the starting point
- If no: identify what's unclear or risky, and what research or clarification would unblock progress

Keep this short — 2-4 sentences.

## What to Avoid

- Don't add deployment, hosting, or DevOps epics at this stage
- Don't list epics that can't be started until halfway through the project as if they're independent
- Don't be vague about technology choices — if you're unsure, pick a sensible default and say so
- Don't pad the domain model with every possible attribute — focus on relationships and any non-obvious fields
- Don't justify a technology choice on performance or scalability grounds unless the user has indicated that's a concern
- Don't introduce infrastructure components (Redis, queues, etc.) to solve problems that a database and simple HTTP patterns can handle at startup scale

## kanban.db Integration

The `architect` skill uses `kanban.db` to track architectural epics, technical design, and acceptance criteria. Each ticket in the database should include:

- **Technical Design**: A detailed description of the technical approach, including stack choices, domain model, and infrastructure.
- **Technical Acceptance Criteria**: Specific, observable outcomes that validate the technical implementation.

### Workflow Adjustments

1. **After Defining Epics**:
   - Use `kanban.py` to add or update tickets with technical design and acceptance criteria.
   - Example:
     ```bash
     python scripts/kanban.py add \
       --name "Define Data Layer" \
       --status PLANNED --version V1 \
       --elaboration "Set up PostgreSQL database schema and migrations for core domain objects." \
       --criteria "Database schema is defined and migrations are testable.\n     Core API endpoints are scaffolded and functional."
     ```

2. **Collaboration with Developer Skill**:
   - Update ticket statuses to reflect progress, e.g., moving from `PLANNED` to `IN PROGRESS` when the developer starts work.
   - Example:
     ```bash
     python scripts/kanban.py update <ticket-id> --status "IN PROGRESS"
     ```

3. **Summary and Handoff**:
   - Use `kanban.py summary` to review the current state of architectural epics before handing off to the `developer` skill.

## What This Skill Does Not Do

**No implementation.** This skill produces an architectural plan — stack choices, domain model, and epics. It never writes application code to the codebase, never creates or modifies source files, and never starts building. Code snippets are fine when they illustrate a design decision (e.g., a schema definition or an interface shape), but they live in the output document, not in the project.

**Architecture is this skill's file.** If the project uses an `ARCH.md` or similar, that belongs here. Read `PO.md` if present — it's the product owner's domain and carries the brief and backlog. Don't write to it.
