# Approved Proposals — Gray Ocean Ideas

> Base framework changes that have been approved and implemented (or ready for implementation).
> Each entry comes from `pending_ideas.md` after review.

---

## [APPROVED] Direct agent invocation via @mention
Proposal date: 2026-02-22
Implementation date: 2026-02-22
Implemented by: human (via Cursor)
Modified files: gray_ocean.py, core/runtime.py, agents/architect/system_prompt.md, tools/spawn_agent.py
Summary: Agents can be invoked with @agent_name message. Names normalized to lowercase. System prompt reinforced to prevent LLM from faking actions without calling tools.
