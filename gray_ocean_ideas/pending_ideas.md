# Pending Proposals — Gray Ocean Ideas

> This file is EXCLUSIVELY for proposing changes to the Gray Ocean framework codebase.
> This includes: `core/runtime.py`, `VALUES.md`, folder structure, system conventions.
>
> Do NOT use this file for: tool creation (use `register_tool`),
> agent creation (use `spawn_agent`), or general tasks.

## Proposal Format

```
## [PROPOSAL] Name of the change
Date: YYYY-MM-DD
Proposed by: agent_name
Affected file(s): core/runtime.py | VALUES.md | folder structure
Observed problem: objective description of the problem in the base framework
Proposed change: what exactly should change in the code
Expected impact: what improves system-wide
Risks: what could break
Complexity: low / medium / high
```

---

## [PROPOSAL] Router Agent — Central Message Routing
Date: 2025-01-09
Proposed by: Architect
Affected file(s): core/runtime.py | folder structure
Observed problem: Currently, all messages go directly to the Architect. There is no triage layer to decide which agent should handle each type of message. This limits scalability and causes the Architect to be triggered even for simple tasks that other agents could resolve.
Proposed change: Create a "Router Agent" that receives ALL human messages and decides:
1. If it's a gray ocean build/extension task → send to Architect
2. If it's casual conversation/general question → send to my_chat_bot
3. If it's something simple the Router can answer directly → respond without triggering another agent
4. If it's specialized (e.g., code, analysis) → send to the appropriate specialist agent

Expected impact:
- Reduces Architect load for simple tasks
- Improves user experience with faster responses for simple cases
- Enables scalability: new agents can be added to routing
- Clear separation of responsibilities

Risks:
- Adds an extra processing layer
- Router may route incorrectly
- Requires well-defined decision logic

Complexity: medium<<<------

## [PROPOSAL] Evolution Agent — Autonomous System Evolution Exploration
Date: 2025-01-09
Proposed by: Architect (requested by human)
Affected file(s): folder structure (new agent)
Observed problem: Currently, gray ocean evolves only in response to explicit human demands or immediate Architect needs. There is no dedicated agent to proactively explore ways to improve the system, identify inefficiency patterns, or propose architectural evolutions. The Architect, focused on resolving requests, does not have bandwidth for deep reflection on framework evolution.

Proposed change: Create an "Evolution Agent" with the mission of:
1. Observing the system in operation (reading logs, analyzing tool usage patterns)
2. Identifying improvement opportunities following the values in VALUES.md
3. Reasoning about proposals before submitting them — evaluating impact, risks, alignment with the constitution
4. Proposing changes via `gray_ocean_ideas/pending_ideas.md` with well-founded analyses
5. NOT implementing changes directly — only proposing with documented reasoning

The agent would strictly follow:
- VALUES.md (especially: Simplicity, Incremental Evolution, Safe Failure)
- Least Privilege: access only to read tools and append_file
- Intentional Immutability: never modifies base code directly

Expected impact:
- Proactive system evolution, not just reactive
- Better thought-out proposals, with explicit reasoning
- Architect can focus on building, while Evolution focuses on reflection
- History of evolution reasoning in human-readable logs

Risks:
- Evolution Agent may generate many low-quality proposals
- May propose changes that don't align with real human needs
- Requires a feedback mechanism to learn what is valuable

Complexity: medium
