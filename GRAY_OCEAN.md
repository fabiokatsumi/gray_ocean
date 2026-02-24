# GRAY_OCEAN — Manifesto

> *An operating system for AI agents inspired by Unix philosophy, where humans describe in natural language and agents solve, evolve, and govern themselves.*

---

## What is Gray Ocean?

Gray Ocean is a self-evolving agent framework. It starts as a "puddle" — a minimal set of tools and a single agent — and grows organically as needs arise.

## Philosophy

Inspired by Unix:
- **Agents** are processes — they do one thing and do it well
- **Tools** are programs — each with a clear function
- **Markdown files** are the filesystem — readable by both humans and agents
- **The Runtime** is the kernel — simple, stable, intentionally limited

## Core Principles

1. **Simplicity** — The minimum necessary, never more
2. **Transparency** — All state is readable in `.md` files
3. **Controlled self-modification** — The system grows, but with rules
4. **Human as arbiter** — Critical decisions go through humans

## How It Works

1. Human sends a message in natural language
2. The Runtime loads the Architect agent
3. The Architect reasons and uses tools to resolve the request
4. If tools are missing, the Architect creates them
5. If the task is recurring, the Architect creates a specialized agent
6. Gray Ocean grows — ready for the next request

## Structure

```
gray_ocean/
├── core/          ← kernel (ReAct loop runtime)
├── tools/         ← available tools
├── agents/        ← system agents
├── gray_ocean_ideas/  ← framework change proposals
├── VALUES.md      ← system constitution
├── GUIDE.md       ← guide for humans and agents
└── gray_ocean.py  ← entry point
```

## Gray Ocean starts as a puddle. The agents decide what it becomes.
