# Sunculture Analytics UI

React + Vite chat client for the AI platform streaming API. Assistant and user messages render as **Markdown** (GFM: tables, lists, code blocks). Renders Apache ECharts when the agent calls `create_echarts_chart` or `create_echarts_portfolio_preset`.

## Prerequisites

- API running: `python3.11 -m uvicorn src.deployment.api.app:app --reload --port 8000`
- Part 2 data (optional, for presets): `python3.11 scripts/run_part2_pipeline.py`
- `OPENAI_API_KEY` set for live agent runs

## Development

```powershell
cd src/ui
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/api/ai` to port 8000.

## Example prompts

- "Use create_echarts_portfolio_preset with arrears_by_country and explain the chart."
- "Chart segment sizes and arrears, then recommend a Kenya marketing segment."

## Build

```powershell
npm run build
npm run preview
```
