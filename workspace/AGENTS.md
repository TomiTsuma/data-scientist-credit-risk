# Sunculture AI Agents

OpenClaw-style agent definitions live in `workspace/agents/*.md`. The streaming assistant loads those files plus this document at runtime.

## Orchestration model

1. **Intent** — Classify the user request (portfolio KPIs, segmentation, marketing, credit risk, executive summary).
2. **Plan** — Use the `planning-with-files` skill; write `task_plan.md`, `findings.md`, `progress.md` under the **session workspace** only.
3. **Execute** — Call MCP tools (data, reports, ClickHouse) and optional `run_command` for `python3.11` analysis scripts in the session folder.
4. **Deliver** — Markdown or structured JSON answer grounded in tool output; link to relevant `reports/` artifacts when they exist.

## Specialist agents (markdown)

| Agent | File | Focus |
|-------|------|--------|
| Customer Analytics | `agents/customer-analytics.md` | Segmentation, cohort KPIs, segment profiles |
| Growth Operations | `agents/growth-operations.md` | Sales trends, lead sources, installation delays |
| Credit & Collections | `agents/credit-risk.md` | Arrears, default proxies, collection actions |
| Marketing Strategy | `agents/marketing-strategy.md` | Kenya premium loan targeting, campaigns |

Invoke the specialist whose description best matches the user question. Use tools before narrating metrics.
