"""
runtime.py — The Gray Ocean Kernel

Implements the ReAct loop (Reason + Act) for agent execution.

Flow:
1. Load the agent from its .md files
2. Build the system prompt injecting personality + available tools
3. Send the human's message to the LLM
4. Parse the response: is it TOOL or DONE?
5. If TOOL: execute the tool, inject result, go back to step 3
6. If DONE: log the action, return response to human
7. If max_steps reached: return what we have and log the timeout
"""

import os
import sys
import json
import importlib.util
from datetime import datetime

# --- LLM Provider config ---
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    env = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

ENV = load_env()
LLM_PROVIDER = ENV.get("LLM_PROVIDER", "ollama").lower()
OLLAMA_HOST = ENV.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = ENV.get("OLLAMA_MODEL", "llama3.1:8b")
OPENAI_API_KEY = ENV.get("OPENAI_API_KEY")
OPENAI_MODEL = ENV.get("OPENAI_MODEL", "gpt-4")
OPENROUTER_API_KEY = ENV.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = ENV.get("OPENROUTER_MODEL", "meta-llama-3")

# Gray Ocean root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")

MAX_STEPS = 15

# In-memory caches — populated once per process, avoid re-reading files on every invocation
_agent_cache: dict = {}
_tool_module_cache: dict = {}
_system_prompt_cache: dict = {}
_values_cache: str = None


def load_agent(agent_name: str) -> dict:
    """Loads an agent from its .md files (cached per process)."""
    agent_name = agent_name.lower().strip()
    if agent_name in _agent_cache:
        return _agent_cache[agent_name]

    agent_dir = os.path.join(AGENTS_DIR, agent_name)

    if not os.path.isdir(agent_dir):
        raise FileNotFoundError(f"Agent '{agent_name}' not found in {agent_dir}")

    agent = {"name": agent_name, "dir": agent_dir}

    md_files = {
        "readme": "README.md",
        "personality": "personality.md",
        "system_prompt": "system_prompt.md",
        "tools": "tools.md",
        "log": "log.md",
    }

    for key, filename in md_files.items():
        filepath = os.path.join(agent_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                agent[key] = f.read()
        else:
            agent[key] = ""

    _agent_cache[agent_name] = agent
    return agent


def parse_authorized_tools(tools_md: str) -> list:
    """Extracts the list of authorized tools from the agent's tools.md."""
    tools = []
    for line in tools_md.split("\n"):
        line = line.strip()
        if line.startswith("- `") and line.endswith("`"):
            tool_name = line[3:-1]
            tools.append(tool_name)
    return tools


def load_tool(tool_name: str):
    """Dynamically loads a tool module (cached per process)."""
    if tool_name in _tool_module_cache:
        return _tool_module_cache[tool_name]

    tool_path = os.path.join(TOOLS_DIR, f"{tool_name}.py")

    if not os.path.exists(tool_path):
        return None

    spec = importlib.util.spec_from_file_location(tool_name, tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _tool_module_cache[tool_name] = module
    return module


def build_tools_description(tool_names: list) -> str:
    """Builds the description of available tools for the system prompt."""
    descriptions = []

    for name in tool_names:
        module = load_tool(name)
        if module:
            desc = getattr(module, "TOOL_DESCRIPTION", "No description")
            params = getattr(module, "TOOL_PARAMETERS", {})
            params_str = "\n".join(f"    {k}: {v}" for k, v in params.items())
            descriptions.append(
                f"### {name}\n{desc}\nParameters:\n{params_str}"
            )

    return "\n\n".join(descriptions)


def build_system_prompt(agent: dict, tool_names: list) -> str:
    """Builds the complete system prompt for the agent (cached per agent+tools combo)."""
    global _values_cache
    cache_key = agent["name"] + "|" + ",".join(sorted(tool_names))
    if cache_key in _system_prompt_cache:
        return _system_prompt_cache[cache_key]

    tools_desc = build_tools_description(tool_names)

    # Load VALUES.md once per process
    if _values_cache is None:
        values_path = os.path.join(BASE_DIR, "VALUES.md")
        if os.path.exists(values_path):
            with open(values_path, "r", encoding="utf-8") as f:
                _values_cache = f.read()
        else:
            _values_cache = ""
    values = _values_cache

    prompt = f"""{agent.get('system_prompt', '')}

---
## Personality
{agent.get('personality', '')}

---
## Available Tools
{tools_desc}

---
## Tool Usage Format

When you need to use a tool, respond EXACTLY in this format (one tool at a time):

TOOL: tool_name
ARGS:
param1: value1
param2: value2

For multi-line arguments, use the <<<>>> delimiter:

TOOL: tool_name
ARGS:
param1: simple value
param2: <<<
content with
multiple lines
here
>>>

When the task is completely done, respond with:

DONE: your final response here

---
## MANDATORY RULE — Real actions only via TOOL

You do NOT have the ability to modify files, create agents, or execute code on your own.
The ONLY way to perform actions is by calling a TOOL with the format above.
If the request requires writing/modifying/creating something, you MUST emit TOOL: before responding DONE:.
Reading a file (read_file) is NOT modifying it. If the request is to add content, call append_file or write_file.
NEVER respond DONE: saying something was done if you did not call the corresponding TOOL.

---
## System Values
{values}
"""
    _system_prompt_cache[cache_key] = prompt
    return prompt


def parse_llm_response(response: str) -> dict:
    """Parses the LLM response to identify TOOL or DONE."""
    response = response.strip()

    # Check for DONE
    if "DONE:" in response:
        idx = response.index("DONE:")
        return {
            "type": "DONE",
            "content": response[idx + 5:].strip(),
            "reasoning": response[:idx].strip() if idx > 0 else "",
        }

    # Check for TOOL
    if "TOOL:" in response:
        idx = response.index("TOOL:")
        reasoning = response[:idx].strip() if idx > 0 else ""
        rest = response[idx:]

        lines = rest.split("\n")
        tool_name = lines[0].replace("TOOL:", "").strip()

        args = {}
        if len(lines) > 1:
            i = 1
            # Skip "ARGS:" line if present
            if i < len(lines) and lines[i].strip().upper().startswith("ARGS"):
                i += 1

            current_key = None
            multiline_value = None
            in_multiline = False

            while i < len(lines):
                line = lines[i]

                if in_multiline:
                    if line.strip() == ">>>":
                        args[current_key] = multiline_value
                        in_multiline = False
                        current_key = None
                        multiline_value = None
                    else:
                        if multiline_value:
                            multiline_value += "\n" + line
                        else:
                            multiline_value = line
                elif ":" in line and not line.startswith(" " * 4):
                    # New key:value pair
                    colon_idx = line.index(":")
                    key = line[:colon_idx].strip()
                    value = line[colon_idx + 1:].strip()

                    if key and key not in ("TOOL", "ARGS"):
                        current_key = key
                        if value == "<<<":
                            in_multiline = True
                            multiline_value = ""
                        else:
                            args[key] = value

                i += 1

        return {
            "type": "TOOL",
            "tool": tool_name,
            "args": args,
            "reasoning": reasoning,
        }

    # If neither TOOL nor DONE, treat as implicit DONE
    return {
        "type": "DONE",
        "content": response,
        "reasoning": "",
    }


def execute_tool(tool_name: str, args: dict, authorized_tools: list) -> str:
    """Executes a tool with the provided arguments."""
    if tool_name not in authorized_tools:
        return f"ERROR: Tool '{tool_name}' not authorized for this agent. Authorized tools: {', '.join(authorized_tools)}"

    module = load_tool(tool_name)
    if module is None:
        return f"ERROR: Tool '{tool_name}' not found in tools/."

    if not hasattr(module, "run"):
        return f"ERROR: Tool '{tool_name}' does not have a run() function."

    try:
        # Convert argument types as needed
        import inspect
        sig = inspect.signature(module.run)
        converted_args = {}

        for param_name, param in sig.parameters.items():
            if param_name in args:
                value = args[param_name]
                annotation = param.annotation

                if annotation == list or (
                    hasattr(annotation, "__origin__")
                    and annotation.__origin__ == list
                ):
                    # Try to parse as JSON list
                    if isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            # Try to parse as comma-separated list
                            value = [v.strip() for v in value.split(",")]
                    converted_args[param_name] = value
                elif annotation == int:
                    converted_args[param_name] = int(value)
                elif annotation == float:
                    converted_args[param_name] = float(value)
                elif annotation == bool:
                    converted_args[param_name] = value.lower() in (
                        "true", "1", "yes"
                    )
                else:
                    converted_args[param_name] = value
            elif param.default is not inspect.Parameter.empty:
                pass  # Use the function's default
            else:
                return (
                    f"ERROR: Required parameter '{param_name}' not provided "
                    f"for tool '{tool_name}'."
                )

        result = module.run(**converted_args)
        return str(result)

    except Exception as e:
        return f"ERROR executing tool '{tool_name}': {e}"


def log_action(agent: dict, action: str):
    """Logs an action to the agent's log.md."""
    log_path = os.path.join(agent["dir"], "log.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"\n## {timestamp}\n{action}\n"

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass  # Log should not interrupt execution


def call_llm(system_prompt: str, messages: list, model: str = None) -> str:
    """Calls the LLM via the provider defined in .env, with streaming to stdout."""
    import urllib.request
    import urllib.error
    import requests

    provider = LLM_PROVIDER
    if model is None:
        if provider == "ollama":
            model = OLLAMA_MODEL
        elif provider == "openai":
            model = OPENAI_MODEL
        elif provider == "openrouter":
            model = OPENROUTER_MODEL

    # System prompt sent once as the first message; messages = current session history only
    all_msgs = [{"role": "system", "content": system_prompt}] + messages

    try:
        if provider == "ollama":
            url = f"{OLLAMA_HOST}/api/chat"
            payload = {"model": model, "messages": all_msgs, "stream": True}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}
            )
            full_content = ""
            with urllib.request.urlopen(req, timeout=120) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk.get("message", {}).get("content", "")
                    if delta:
                        print(delta, end="", flush=True)
                        full_content += delta
                    if chunk.get("done", False):
                        break
            print()
            return full_content or "ERROR: Empty response from LLM."

        elif provider in ("openai", "openrouter"):
            if provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                api_key = OPENAI_API_KEY
            else:
                url = "https://openrouter.ai/api/v1/chat/completions"
                api_key = OPENROUTER_API_KEY
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": all_msgs,
                "temperature": 0.7,
                "stream": True,
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=120, stream=True)
            if resp.status_code != 200:
                return f"ERROR: {provider} API {resp.status_code}: {resp.text}"
            full_content = ""
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {}).get("content") or ""
                    if delta:
                        print(delta, end="", flush=True)
                        full_content += delta
                except (json.JSONDecodeError, KeyError, IndexError):
                    pass
            print()
            return full_content or "ERROR: Empty response from LLM."

        else:
            return f"ERROR: LLM_PROVIDER '{provider}' not supported."

    except urllib.error.URLError as e:
        return f"ERROR: Could not connect to LLM. Details: {e}"
    except Exception as e:
        return f"ERROR calling LLM: {e}"


WRITE_TOOLS = {"write_file", "append_file", "register_tool", "spawn_agent"}

WRITE_CLAIM_KEYWORDS = [
    "added", "written", "created", "saved", "registered", "appended",
    "proposal added", "file updated", "file written", "file created",
]

WRITE_REQUEST_KEYWORDS = [
    "add to", "write to", "write in", "append", "create", "save",
    "register", "modify", "update",
]


def _message_requests_write(user_message: str) -> bool:
    """Checks if the user message is asking for a write/modify action."""
    lower = user_message.lower()
    return any(kw in lower for kw in WRITE_REQUEST_KEYWORDS)


def _response_claims_write(response: str) -> bool:
    """Checks if the DONE response claims to have written/modified something."""
    lower = response.lower()
    return any(kw in lower for kw in WRITE_CLAIM_KEYWORDS)


def run_agent(agent_name: str, user_message: str, model: str = None) -> str:
    """
    Runs the complete ReAct loop for an agent.

    1. Load the agent
    2. Build the system prompt
    3. Send message → LLM
    4. Parse response (TOOL or DONE)
    5. If TOOL: execute, inject result, repeat
    6. If DONE: log and return (with hallucination guard)
    7. If max_steps: return with warning
    """
    # 1. Load agent
    agent = load_agent(agent_name)

    # 2. Identify authorized tools
    authorized_tools = parse_authorized_tools(agent.get("tools", ""))

    # 3. Build system prompt
    system_prompt = build_system_prompt(agent, authorized_tools)

    # 4. Start conversation
    messages = [{"role": "user", "content": user_message}]

    log_action(agent, f"- Received message: {user_message[:200]}...")

    # Track which tool categories were actually called
    called_write_tool = False
    hallucination_retries = 0

    # 5. ReAct loop
    for step in range(1, MAX_STEPS + 1):
        # Call LLM
        llm_response = call_llm(system_prompt, messages, model)

        if llm_response.startswith("ERROR:"):
            print(llm_response, file=sys.stderr)
            log_action(agent, f"- ERROR in LLM (step {step}): {llm_response}")
            return llm_response

        # Parse response
        parsed = parse_llm_response(llm_response)

        if parsed["type"] == "DONE":
            final_response = parsed["content"]

            if (
                not called_write_tool
                and hallucination_retries < 2
                and _message_requests_write(user_message)
                and _response_claims_write(final_response)
            ):
                hallucination_retries += 1
                log_action(
                    agent,
                    f"- HALLUCINATION GUARD (step {step}): Agent claimed write "
                    f"without calling a write tool. Retrying. (attempt {hallucination_retries})"
                )
                correction = (
                    "ERROR: You said you performed a write/modify action, "
                    "but NO write tool was called in this session. "
                    "Reading a file (read_file) is NOT the same as modifying it. "
                    "You MUST call write_file or append_file with the correct content "
                    "BEFORE responding DONE. Make the TOOL call now."
                )
                messages.append({"role": "assistant", "content": llm_response})
                messages.append({"role": "user", "content": correction})
                continue

            log_action(
                agent,
                f"- Task completed (step {step})\n- Response: {final_response[:300]}..."
            )
            return final_response

        elif parsed["type"] == "TOOL":
            tool_name = parsed["tool"]
            tool_args = parsed["args"]

            if tool_name in WRITE_TOOLS:
                called_write_tool = True

            log_action(
                agent,
                f"- Step {step}: Tool={tool_name}, Args={json.dumps(tool_args, ensure_ascii=False)[:200]}"
            )

            # Execute tool
            tool_result = execute_tool(tool_name, tool_args, authorized_tools)

            log_action(
                agent,
                f"- Tool result '{tool_name}': {tool_result[:200]}..."
            )

            # Add to conversation
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({
                "role": "user",
                "content": f"Tool result '{tool_name}':\n{tool_result}"
            })

    # Max steps reached
    timeout_msg = (
        f"WARNING: Limit of {MAX_STEPS} steps reached. "
        f"Last conversation state returned."
    )
    log_action(agent, f"- TIMEOUT: {MAX_STEPS} steps reached")
    return timeout_msg
