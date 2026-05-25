# Security

- Do not exfiltrate secrets or `.env` contents.
- `run_clickhouse_select` allows **SELECT only**.
- `read_file` / `write_file` are restricted to the project root and session workspace.
- Do not log or repeat API keys in responses.
