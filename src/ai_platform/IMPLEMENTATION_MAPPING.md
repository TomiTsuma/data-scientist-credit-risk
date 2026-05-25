# Cropnuts-AI to Sunculture Implementation Mapping

This document shows how Cropnuts-AI patterns were applied to Sunculture's AI Platform.

## Pattern Mapping

### 1. Session & Workspace Management

| Cropnuts Pattern | Sunculture Implementation | File |
|---|---|---|
| UUID-based folders: `outputs/{task_id}/` | UUID-based: `workspace/ai_sessions/{session_id}/` | `core/session.py` |
| Subfolders: `data/`, `logs/`, `reports/` | Subfolders: `data/`, `schemas/`, `logs/`, `reports/`, `artifacts/` | `core/session.py` |
| `execution_log.json` | `ExecutionLog` class with JSON serialization | `core/execution_log.py` |
| `context_state.json` | `ContextManager` class with JSON persistence | `core/context.py` |
| Progress logging: `progress.md` | `SessionManager.log_progress()` | `core/session.py` |
| `SESSION_ID=$(cat /tmp/current_session_id.txt)` | Session ID managed in `SessionManager` | `core/session.py` |

### 2. Execution Logging

| Cropnuts | Sunculture | Class |
|---|---|---|
| Execution log tracks: task_id, timestamp, status, user | `ExecutionLog` stores full audit trail | `core/execution_log.py` |
| Data inputs with row/column counts | `log_data_input(source, name, row_count, col_count)` | `ExecutionLog` |
| Transformations with transformation_id | `log_transformation()` with transformation_id UUID | `ExecutionLog` |
| LLM interactions: agent, prompt, response, model, timestamp | `log_llm_interaction()` with tokens, latency | `ExecutionLog` |
| Plan steps with status tracking | `add_plan_step()`, `update_plan_step()` | `ExecutionLog` |
| Errors and warnings | `log_error()`, `log_warning()` | `ExecutionLog` |

### 3. Agent Architecture

| Cropnuts | Sunculture | File |
|---|---|---|
| `BaseAgent` with provider abstraction | `BaseAgent` with async LLM calls | `core/agent.py` |
| Provider: OpenAI, Gemini, Ollama, Claude | Same providers supported | `core/agent.py` |
| `BaseMicroAgent` for domain-specific tasks | `MicroAgent` class | `core/agent.py` |
| Agent receives context envelope | MicroAgent gets context summary | `core/agent.py` |
| Agent logs to execution_log | `call_llm()` logs interactions | `core/agent.py` |
| Skill injection | `register_skill()`, `get_skill()` | `core/agent.py` |

### 4. Skills System

| Cropnuts | Sunculture | File |
|---|---|---|
| `DataSkill` - fetch + transform | `DataSkill` base + `SunCultureDataSkill` | `core/skills.py`, `skills/concrete_skills.py` |
| `VisualizationSkill` - chart generation | `VisualizationSkill` base + `SunCultureVisualizationSkill` | `core/skills.py`, `skills/concrete_skills.py` |
| `ReportSkill` - markdown assembly | `ReportSkill` base + `SunCultureReportSkill` | `core/skills.py`, `skills/concrete_skills.py` |
| `IntentClassificationSkill` - task routing | `IntentClassificationSkill` base class | `core/skills.py` |
| Skills log transformations | Skills call `log_transformation()` on ExecutionLog | `skills/concrete_skills.py` |
| Stateless, reusable skills | Skills are pure Python classes | `core/skills.py` |

### 5. Task System

| Cropnuts | Sunculture | File |
|---|---|---|
| `LimsExecutiveSummaryTask` | `@Task.register()` decorator pattern | `core/task.py` |
| 4-phase execution | Same phases: Plan → Context → Execute → Finalize | `core/task.py` |
| Multi-agent coordination | Task coordinates MicroAgents | `core/task.py` |
| Task registry: `intent_skill.classify_intent()` | `Task.get_task()`, `Task.list_tasks()` | `core/task.py` |
| Plan steps with status | `add_plan_step()`, `execute_plan_step()` | `core/task.py` |
| Micro-agent execution | `execute_plan_step()` runs agents | `core/task.py` |

### 6. Context Management

| Cropnuts | Sunculture | File |
|---|---|---|
| `ContextManager` maintains state | Same `ContextManager` class | `core/context.py` |
| Tracks: client_name, farm_info, completed_sections | Tracks: metadata, completed_sections, narrative | `core/context.py` |
| `running_narrative` building | Same narrative assembly | `core/context.py` |
| Tracks artifacts (diagrams, charts) | `artifacts` dict per section | `core/context.py` |
| `get_context_summary()` for micro-agents | Same method signature | `core/context.py` |
| `save_state()` to JSON | `_save()` persists to context.json | `core/context.py` |

### 7. LLM Service

| Cropnuts | Sunculture | File |
|---|---|---|
| Provider abstraction: openai, gemini, ollama | Same abstraction | `core/agent.py` |
| `LLMService` initialization per provider | Providers initialized in `BaseAgent.__init__()` | `core/agent.py` |
| Streaming support | `call_llm(..., stream=True)` | `core/agent.py` |
| Error recovery | Try-catch with error logging | `core/agent.py` |
| Prompt registry: `get_prompt(agent, task)` | `config/prompts.py` with registry | `config/prompts.py` |

### 8. Configuration Management

| Cropnuts | Sunculture | File |
|---|---|---|
| `config/prompts/prompts.py` - prompt registry | `config/prompts.py` - unified registry | `config/prompts.py` |
| `config/llm_config.yaml` - LLM settings | Env vars in `config.py` | `config.py` |
| Agent registry | `config/agents.py` - agent definitions | `config/agents.py` |
| Task registry | `config/tasks.py` - task definitions | `config/tasks.py` |

### 9. Concrete Implementations

| Cropnuts | Sunculture | File |
|---|---|---|
| `SoilAnalysisAgent`, `WaterAnalysisAgent` | `CustomerAnalysisAgent`, `GrowthOperationsAgent` | `agents/concrete_agents.py` |
| `LimsExecutiveSummaryTask` | `CustomerSegmentationTask`, `GrowthPlanningTask` | `tasks/concrete_tasks.py` |
| Skill implementations | `SunCulture*Skill` classes | `skills/concrete_skills.py` |
| Prompt templates in YAML | Python dict-based prompts | `config/prompts.py` |

## Deviations & Enhancements

### 1. **Async/Await**
- Cropnuts uses synchronous agent calls
- Sunculture uses `async`/`await` for scalability
- `BaseAgent.call_llm()` is async with streaming

### 2. **Configuration**
- Cropnuts: YAML files + Python code mixed
- Sunculture: Centralized Python-based config for prompts, agents, tasks

### 3. **Provider Handling**
- Cropnuts: Provider-specific logic in `__getattr__` delegation
- Sunculture: Explicit provider initialization, cleaner abstraction

### 4. **Execution Log**
- Cropnuts: Generic JSON structure
- Sunculture: Structured dataclasses + comprehensive logging

### 5. **Context Manager**
- Cropnuts: Context-specific to agronomy domain
- Sunculture: Generic context manager for any domain

### 6. **Skills Registration**
- Cropnuts: Skills instantiated in agent
- Sunculture: Explicit skill registration pattern

## Quick Reference: File Locations

### Cropnuts Originals
```
cropnuts-ai/
  agents/base_agent.py              → core/agent.py (BaseAgent)
  agents/agronomy_agent/main.py     → core/task.py (Task pattern)
  agents/agronomy_agent/context.py  → core/context.py
  agents/agronomy_agent/skills/     → core/skills.py
  config/prompts/prompts.py         → config/prompts.py
  providers/llm_service.py          → core/agent.py (LLMService pattern)
  tasks/lims_executive_summary.py   → tasks/concrete_tasks.py
```

### Sunculture Implementations
```
src/ai_platform/
  core/
    agent.py                  ← BaseAgent, MicroAgent, LLM service
    session.py               ← SessionManager with execution_log/context
    execution_log.py         ← Execution log with audit trail
    context.py              ← ContextManager for state
    skills.py               ← Skill base classes
    task.py                 ← Task base class with registry
  
  agents/
    concrete_agents.py       ← CustomerAnalysisAgent, GrowthOperationsAgent, etc.
  
  skills/
    concrete_skills.py       ← SunCultureDataSkill, VisualizationSkill, etc.
  
  tasks/
    concrete_tasks.py        ← CustomerSegmentationTask, GrowthPlanningTask, etc.
  
  config/
    prompts.py              ← Prompt registry
    agents.py               ← Agent definitions
    tasks.py                ← Task definitions
```

## How to Extend

### 1. Add New Agent
```python
class MyNewAgent(MicroAgent):
    def __init__(self, ...):
        super().__init__(
            name="my_agent",
            task_type="my_task_type",
            ...
        )
        self.register_skill("skill_name", SkillClass())
    
    async def _perform_task(self, input_data, **kwargs):
        ...
```

### 2. Add New Skill
```python
class MyNewSkill(Skill):  # or inherit from DataSkill, AnalysisSkill, etc.
    def execute(self, **kwargs):
        ...
        if self.execution_log:
            self.log_transformation(...)
```

### 3. Add New Task
```python
@Task.register("my_task_name")
class MyNewTask(Task):
    def __init__(self, session_manager, session_id=None):
        super().__init__("my_task_name", session_manager, session_id)
        # Register agents, add plan steps
    
    async def _gather_context(self, input_data):
        ...
    
    async def _finalize(self, input_data):
        ...
```

### 4. Register New Prompt
```python
# config/prompts.py
PROMPTS["my_agent"] = {
    "my_task": "Prompt template with {placeholder}"
}
```

## Testing the Implementation

```python
# 1. Create session
from pathlib import Path
from src.ai_platform.core.session import SessionManager

workspace = Path("workspace/ai_sessions")
session_mgr = SessionManager(workspace)
session_mgr.create_session(task_name="customer_segmentation")

# 2. Check execution log
print(session_mgr.execution_log.to_dict())

# 3. Check context
print(session_mgr.context_manager.to_dict())

# 4. Get task
from src.ai_platform.core.task import Task
task = Task.get_task("customer_segmentation", session_manager=session_mgr)

# 5. Execute task
result = await task.execute_workflow({...})

# 6. Verify outputs
# - workspace/ai_sessions/{session_id}/execution_log.json
# - workspace/ai_sessions/{session_id}/context.json
# - workspace/ai_sessions/{session_id}/workspace/reports/
# - workspace/ai_sessions/{session_id}/workspace/artifacts/
```
