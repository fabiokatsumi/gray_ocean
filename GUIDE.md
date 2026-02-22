# GUIDE.md — Guia do Gray Ocean

> Guia para humanos e agentes interagirem com o Gray Ocean.

---

## Para Humanos

### Como usar

```bash
# Configurar o ambiente (primeira vez)
bash setup.sh

# Enviar uma mensagem ao Architect
python gray_ocean.py "sua mensagem aqui"

# Exemplos
python gray_ocean.py "liste todas as tools disponíveis"
python gray_ocean.py "crie uma tool que calcula fibonacci"
python gray_ocean.py "preciso de um agente que monitora arquivos"
```

### O que acontece quando você envia uma mensagem?

1. O `gray_ocean.py` recebe sua mensagem
2. O `core/runtime.py` carrega o agente Architect
3. O Architect raciocina sobre como resolver sua solicitação
4. Ele usa tools conforme necessário (ler arquivos, executar código, etc.)
5. Se precisa de algo que não existe, ele cria (tool ou agente)
6. Você recebe a resposta final

### Como verificar o que aconteceu?

- Leia `agents/architect/log.md` para ver todas as ações do Architect
- Leia `tools/index.md` para ver todas as tools disponíveis
- Liste `agents/` para ver todos os agentes existentes

### Como auditar o sistema?

Todo estado do Gray Ocean é armazenado em arquivos Markdown legíveis:
- Cada agente tem um `log.md` com histórico completo
- O `tools/index.md` cataloga todas as ferramentas
- `gray_ocean_ideas/` mostra propostas de mudança no framework

---

## Para Agentes

### Convenções

1. **Toda ação deve ser registrada** no `log.md` do agente
2. **Verifique o que existe antes de criar** — leia `tools/index.md`
3. **Use apenas tools autorizadas** — listadas no seu `tools.md`
4. **Siga os valores** — leia e respeite `VALUES.md`
5. **Formato de resposta** — use TOOL/DONE conforme definido no system_prompt.md

### Como criar uma tool

1. Escreva o código Python com uma função `run()` e docstring
2. Teste com `run_python` para validar
3. Registre com `register_tool` para tornar disponível

### Como criar um agente

Use a tool `spawn_agent` com:
- `name`: nome do agente
- `purpose`: missão/propósito
- `tools`: lista de tools que o agente precisa
- `personality` (opcional): traços de personalidade

### Propostas de mudança no framework

Para propor mudanças em `core/`, `VALUES.md`, ou na estrutura de pastas:
1. Escreva a proposta em `gray_ocean_ideas/pending_ideas.md`
2. Siga o formato padronizado
3. Aguarde aprovação antes de implementar

> Mudanças em tools e agentes NÃO precisam de proposta — crie diretamente.
