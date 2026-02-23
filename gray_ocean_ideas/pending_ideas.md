# Propostas Pendentes — Gray Ocean Ideas

> Este arquivo é EXCLUSIVO para propor mudanças no código base do Gray Ocean framework.
> Isso inclui: `core/runtime.py`, `VALUES.md`, estrutura de pastas, convenções do sistema.
>
> NÃO use este arquivo para: criação de tools (use `register_tool`),
> criação de agentes (use `spawn_agent`), ou tarefas gerais.

## Formato de Proposta

```
## [PROPOSTA] Nome da mudança
Data: YYYY-MM-DD
Proposta por: nome_do_agente
Arquivo(s) afetado(s): core/runtime.py | VALUES.md | estrutura de pastas
Problema observado: descrição objetiva do problema no framework base
Mudança proposta: o que exatamente deveria mudar no código
Impacto esperado: o que melhora no sistema como um todo
Riscos: o que pode quebrar
Complexidade: baixa / média / alta
```

---

## [PROPOSTA] Router Agent — Roteamento Central de Mensagens
Data: 2025-01-09
Proposta por: Architect
Arquivo(s) afetado(s): core/runtime.py | estrutura de pastas
Problema observado: Atualmente, todas as mensagens chegam diretamente ao Architect. Não há camada de triagem para decidir qual agente deve lidar com cada tipo de mensagem. Isso limita a escalabilidade e faz o Architect ser acionado até para tarefas simples que outros agentes poderiam resolver.
Mudança proposta: Criar um "Router Agent" que recebe TODAS as mensagens do humano e decide:
1. Se é uma tarefa de construção/extensão do gray ocean → enviar ao Architect
2. Se é uma conversa casual/pergunta geral → enviar ao my_chat_bot
3. Se é algo simples que o Router pode responder diretamente → responder sem acionar outro agente
4. Se é especializado (ex: código, análise) → enviar ao agente especialista apropriado

Impacto esperado: 
- Reduz carga no Architect para tarefas simples
- Melhora experiência do usuário com respostas mais rápidas para casos simples
- Permite escalabilidade: novos agentes podem ser adicionados ao roteamento
- Separação clara de responsabilidades

Riscos: 
- Adiciona uma camada extra de processamento
- Router pode fazer roteamento incorreto
- Necessita lógica de decisão bem definida

Complexidade: média<<<------

## [PROPOSTA] Evolution Agent — Exploração Autônoma de Evolução do Sistema
Data: 2025-01-09
Proposta por: Architect (solicitado por humano)
Arquivo(s) afetado(s): estrutura de pastas (novo agente)
Problema observado: Atualmente, o gray ocean evolui apenas em resposta a demandas explícitas do humano ou necessidades imediatas do Architect. Não há um agente dedicado a explorar proativamente formas de melhorar o sistema, identificar padrões de ineficiência, ou propor evoluções arquiteturais. O Architect, focado em resolver pedidos, não tem bandwidth para reflexão profunda sobre a evolução do framework.

Mudança proposta: Criar um "Evolution Agent" com a missão de:
1. Observar o sistema em funcionamento (lendo logs, analisando padrões de uso de tools)
2. Identificar oportunidades de melhoria seguindo os valores do VALUES.md
3. Racicionar sobre propostas antes de submetê-las — avaliando impacto, riscos, alinhamento com a constituição
4. Propor mudanças via `gray_ocean_ideas/pending_ideas.md` com análises bem fundamentadas
5. NÃO implementar mudanças diretamente — apenas propor com raciocínio documentado

O agente seguiria rigorosamente:
- VALUES.md (especialmente: Simplicidade, Evolução Incremental, Falha Segura)
- Menor Privilégio: acesso apenas a tools de leitura e append_file
- Imutabilidade Intencional: nunca modifica código base diretamente

Impacto esperado:
- Evolução proativa do sistema, não apenas reativa
- Propostas mais bem pensadas, com raciocínio explícito
- O Architect pode focar em construção, enquanto Evolution foca em reflexão
- Histórico de raciocínio sobre evolução em logs legíveis por humanos

Riscos:
- Evolution Agent pode gerar muitas propostas de baixa qualidade
- Pode propor mudanças que não alinham com necessidades reais do humano
- Necessita mecanismo de feedback para aprender o que é valioso

Complexidade: média