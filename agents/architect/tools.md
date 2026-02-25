# Authorized Tools — Architect

This agent has access to ALL 9 primitive tools:

- `read_file`
- `write_file`
- `append_file`
- `list_dir`
- `run_python`
- `ask_llm`
- `register_tool`
- `spawn_agent`
- `send_message`

> The Architect is the only agent with full access.
> Agents created by it will receive ONLY the tools necessary for their mission.
> Least privilege principle: broad access for the builder, restricted for the inhabitants.
