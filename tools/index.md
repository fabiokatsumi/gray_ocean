# Tools Index — Gray Ocean

> Catalog of all tools available in Gray Ocean.
> Automatically updated when new tools are registered via `register_tool`.

---

## Primitive Tools (built-in)

### `read_file`
- **File:** `tools/read_file.py`
- **Description:** Reads the content of a file in gray ocean
- **Parameters:** `path` (relative path to the file)
- **Unix analog:** `cat`

### `write_file`
- **File:** `tools/write_file.py`
- **Description:** Creates or overwrites a file in gray ocean
- **Parameters:** `path` (relative path), `content` (content to write)
- **Unix analog:** `echo >`

### `append_file`
- **File:** `tools/append_file.py`
- **Description:** Appends content to the end of an existing file
- **Parameters:** `path` (relative path), `content` (content to append)
- **Unix analog:** `echo >>`

### `list_dir`
- **File:** `tools/list_dir.py`
- **Description:** Lists the content of a directory
- **Parameters:** `path` (relative path, default: root)
- **Unix analog:** `ls`

### `run_python`
- **File:** `tools/run_python.py`
- **Description:** Executes Python code in an isolated sandbox
- **Parameters:** `code` (Python code to execute)
- **Unix analog:** `exec / subprocess`

### `ask_llm`
- **File:** `tools/ask_llm.py`
- **Description:** Makes a call to the LLM via local Ollama
- **Parameters:** `prompt` (message), `system` (optional), `model` (optional, default: llama3.1)
- **Unix analog:** `curl` for API

### `register_tool`
- **File:** `tools/register_tool.py`
- **Description:** Registers a new tool in gray ocean (saves .py and updates index)
- **Parameters:** `name` (name), `code` (code with run()), `description` (description)
- **Unix analog:** `install`

### `spawn_agent`
- **File:** `tools/spawn_agent.py`
- **Description:** Creates a new agent with folder and 5 .md files
- **Parameters:** `name` (name), `purpose` (mission), `tools` (list of tools), `personality` (optional)
- **Unix analog:** `fork + mkdir`

### `send_message`
- **File:** `tools/send_message.py`
- **Description:** Sends a message to another agent and returns its response. All traffic is logged to messages.md.
- **Parameters:** `to` (target agent name), `message` (message to send)
- **Unix analog:** `pipe` (|)

---

## Tools Created by Agents

> New tools will appear below as they are registered via `register_tool`.
