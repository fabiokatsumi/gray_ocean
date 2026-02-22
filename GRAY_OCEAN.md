# GRAY_OCEAN — Manifesto

> *Um sistema operacional para agentes de IA inspirado na filosofia Unix, onde humanos descrevem em linguagem natural e agentes resolvem, evoluem e se governam.*

---

## O que é o Gray Ocean?

O Gray Ocean é um framework de agentes auto-evolutivos. Ele começa como uma "poça d'água" — um conjunto mínimo de ferramentas e um único agente — e cresce organicamente conforme as necessidades surgem.

## Filosofia

Inspirado no Unix:
- **Agentes** são processos — fazem uma coisa e fazem bem
- **Tools** são programas — cada uma com uma função clara
- **Arquivos Markdown** são o filesystem — legíveis por humanos e agentes
- **O Runtime** é o kernel — simples, estável, intencionalmente limitado

## Princípios Fundamentais

1. **Simplicidade** — O mínimo necessário, nunca mais
2. **Transparência** — Todo estado é legível em `.md`
3. **Auto-modificação controlada** — O sistema cresce, mas com regras
4. **Humano como árbitro** — Decisões críticas passam por humanos

## Como Funciona

1. Humano envia mensagem em linguagem natural
2. O Runtime carrega o agente Architect
3. O Architect raciocina e usa tools para resolver
4. Se faltam tools, o Architect as cria
5. Se a tarefa é recorrente, o Architect cria um agente especializado
6. O Gray Ocean cresce — pronto para o próximo pedido

## Estrutura

```
gray_ocean/
├── core/          ← kernel (runtime do loop ReAct)
├── tools/         ← ferramentas disponíveis
├── agents/        ← agentes do sistema
├── gray_ocean_ideas/  ← propostas de mudança no framework
├── VALUES.md      ← constituição do sistema
├── GUIDE.md       ← guia para humanos e agentes
└── gray_ocean.py  ← ponto de entrada
```

## O Gray Ocean começa como uma poça. Os agentes decidem o que ele se torna.
