# Tools & Skills

## MCP data tools

- `get_portfolio_kpis` — Portfolio health by country and payment type
- `query_customers` — Filter customers; sample rows + summary
- `list_customer_segments` / `predict_customer_segment` — Segmentation (Part 2)
- `read_business_report` — Official markdown reports under `reports/`
- `run_clickhouse_select` — Read-only SQL on `sunculture_db` when ClickHouse is up

## Workspace tools

- `list_skills` / `read_skill` — OpenClaw skills under `workspace/skills/`
- `list_document_structures` / `read_document_structure` — Report outlines
- `list_knowledge` / `read_knowledge` — Domain reference docs
- `list_agents` / `read_agent` — Specialist agent markdown
- `get_session_folder_structure` — Inspect session workspace files

## Runtime tools

- `read_file` / `write_file` — Project and session files (relative paths)
- `run_command` — Shell; use `python3.11` for scripts (not `python` or `python3`)
- `platform_info` — Host environment

## Skills (read with `read_skill` before use)

- `planning-with-files` — Required for multi-step analysis
- `portfolio-analytics` — KPIs and filters
- `customer-segmentation` — Clusters and profiles
- `credit-collections` — SMART recommendations
- `executive-data-story` — EDA-style leadership narrative
