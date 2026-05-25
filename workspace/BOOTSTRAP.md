# Bootstrap

On first message in a new session:

1. Confirm whether Part 2 data exists (`get_portfolio_kpis` or `list_customer_segments`).
2. If the task has more than three tool calls, start `planning-with-files` in the session workspace.
3. Load the relevant skill via `read_skill` before deep analysis.
4. For report-style output, check `list_document_structures` and follow the matching structure.

Data refresh (local):

```powershell
python3.11 scripts/run_part2_pipeline.py
```
