# Tools Index — Gray Ocean

> Catálogo de todas as tools disponíveis no Gray Ocean.
> Atualizado automaticamente quando novas tools são registradas via `register_tool`.

---

## Tools Primitivas (built-in)

### `read_file`
- **Arquivo:** `tools/read_file.py`
- **Descrição:** Lê o conteúdo de um arquivo do gray ocean
- **Parâmetros:** `path` (caminho relativo ao arquivo)
- **Analogia Unix:** `cat`

### `write_file`
- **Arquivo:** `tools/write_file.py`
- **Descrição:** Cria ou sobrescreve um arquivo no gray ocean
- **Parâmetros:** `path` (caminho relativo), `content` (conteúdo)
- **Analogia Unix:** `echo >`

### `append_file`
- **Arquivo:** `tools/append_file.py`
- **Descrição:** Adiciona conteúdo ao final de um arquivo existente
- **Parâmetros:** `path` (caminho relativo), `content` (conteúdo a adicionar)
- **Analogia Unix:** `echo >>`

### `list_dir`
- **Arquivo:** `tools/list_dir.py`
- **Descrição:** Lista o conteúdo de um diretório
- **Parâmetros:** `path` (caminho relativo, padrão: raiz)
- **Analogia Unix:** `ls`

### `run_python`
- **Arquivo:** `tools/run_python.py`
- **Descrição:** Executa código Python em sandbox isolada
- **Parâmetros:** `code` (código Python a executar)
- **Analogia Unix:** `exec / subprocess`

### `ask_llm`
- **Arquivo:** `tools/ask_llm.py`
- **Descrição:** Faz uma chamada ao LLM via Ollama local
- **Parâmetros:** `prompt` (mensagem), `system` (opcional), `model` (opcional, padrão: llama3.1)
- **Analogia Unix:** `curl` para API

### `register_tool`
- **Arquivo:** `tools/register_tool.py`
- **Descrição:** Registra uma nova tool no gray ocean (salva .py e atualiza index)
- **Parâmetros:** `name` (nome), `code` (código com run()), `description` (descrição)
- **Analogia Unix:** `install`

### `spawn_agent`
- **Arquivo:** `tools/spawn_agent.py`
- **Descrição:** Cria um novo agente com pasta e 5 arquivos .md
- **Parâmetros:** `name` (nome), `purpose` (missão), `tools` (lista de tools), `personality` (opcional)
- **Analogia Unix:** `fork + mkdir`

---

## Tools Criadas por Agentes

> Novas tools aparecerão abaixo conforme forem registradas via `register_tool`.
