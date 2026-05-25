---
name: planning-with-files
description: Manus/OpenClaw-style planning with task_plan.md, findings.md, and progress.md in the session workspace. Use for any task needing more than five tool calls.
user-invocable: true
metadata:
  openclaw:
    os: ["darwin", "linux", "win32"]
---

# Planning with Files

Use the **session workspace** as disk-backed working memory.

## Files (session workspace only)

| File | Purpose |
|------|---------|
| `task_plan.md` | Phases, output type, success criteria |
| `findings.md` | Metrics and quotes from tools |
| `progress.md` | Timestamped log |

Never write these to `workspace/` root — only under `workspace/sessions/{session_id}/workspace/`.

## Loop

1. Create the three files at task start.
2. Re-read `task_plan.md` before major decisions.
3. Update after each phase; call `get_session_folder_structure` to verify artifacts.
