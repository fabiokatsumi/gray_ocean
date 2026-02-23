# Propostas Aprovadas — Gray Ocean Ideas

> Mudanças no framework base que foram aprovadas e implementadas (ou prontas para implementação).
> Cada entrada vem de `pending_ideas.md` após revisão.

---

## [APROVADA] Invocação direta de agentes via @menção
Data da proposta: 2026-02-22
Data da implementação: 2026-02-22
Implementado por: humano (via Cursor)
Arquivos modificados: gray_ocean.py, core/runtime.py, agents/architect/system_prompt.md, tools/spawn_agent.py
Resumo: Agentes podem ser invocados com @nome_agente mensagem. Nomes normalizados para lowercase. Sistema prompt reforçado para impedir que LLM finja ações sem chamar tools.
