# Tools Autorizadas — Architect

Este agente tem acesso a TODAS as 8 tools primitivas:

- `read_file`
- `write_file`
- `append_file`
- `list_dir`
- `run_python`
- `ask_llm`
- `register_tool`
- `spawn_agent`

> O Architect é o único agente com acesso total.
> Agentes criados por ele receberão APENAS as tools necessárias para sua missão.
> Princípio de menor privilégio: acesso amplo para o construtor, restrito para os habitantes.
