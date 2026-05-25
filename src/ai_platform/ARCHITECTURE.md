# Sunculture AI Platform Architecture

Implemented from Cropnuts-AI patterns - a comprehensive AI agent framework.

## 🏗️ Architecture Overview

The Sunculture AI Platform follows a **hierarchical, task-driven agent system** with the following key components:

### Core Infrastructure

1. **Session Management** (`core/session.py`)
   - UUID-based session identification
   - Structured workspace directories: `data/`, `schemas/`, `logs/`, `reports/`, `artifacts/`
   - File I/O utilities for saving/loading data, reports, and artifacts

2. **Execution Logging** (`core/execution_log.py`)
   - Comprehensive audit trail of all operations
   - Tracks: data inputs, transformations, LLM interactions, errors, warnings
   - JSON-based logging for analysis and debugging
   - Records: timing, token counts, transformation parameters

3. **Context Management** (`core/context.py`)
   - Maintains state across task execution
   - Tracks completed sections and running narrative
   - Stores artifacts (charts, visualizations) per section
   - Provides context summaries for micro-agents
   - LLM interaction logging

### Agent Architecture

1. **BaseAgent** (`core/agent.py`)
   - Provider abstraction: OpenAI, Gemini, Ollama, Claude
   - Unified LLM interface with streaming support
   - Skill composition and registration
   - Error recovery and retry logic

2. **MicroAgent** (`core/agent.py`)
   - Specialized agents for specific tasks
   - Receives context envelope + input data
   - Tracks input/output sections
   - Logs to execution log and context manager

### Skills System

Reusable, stateless components for specific functionality:

1. **Skill Base Class** (`core/skills.py`)
   - Abstract base for all skills
   - Transformation logging support

2. **DataSkill**
   - Data fetching from multiple sources (parquet, CSV, database)
   - Data transformation and normalization
   - Transformation tracking with metadata

3. **VisualizationSkill**
   - Chart generation (line, bar, scatter, histogram)
   - Image export as bytes
   - Brand-consistent styling

4. **ReportSkill**
   - Markdown report assembly
   - Section management
   - Metadata and recommendation integration

5. **AnalysisSkill**
   - Statistical analysis (descriptive, correlation, distribution)
   - Aggregation and grouping
   - Results in standardized format

6. **IntentClassificationSkill**
   - Route user requests to appropriate tasks
   - Task registry management

### Task System

Task-driven workflow orchestration:

1. **Task Base Class** (`core/task.py`)
   - Defines complete execution workflow
   - Multi-phase execution (plan → context → execution → finalize)
   - Micro-agent coordination
   - Plan step management

2. **Task Registry** (`core/task.py`)
   - @Task.register decorator for task registration
   - Dynamic task discovery and routing
   - Task configuration lookup

3. **Phases** (4-phase execution model)
   - **Phase 1**: Plan generation
   - **Phase 2**: Context gathering (metadata, data preparation)
   - **Phase 3**: Micro-agent execution (parallel/sequential)
   - **Phase 4**: Finalization (report generation, output assembly)

## 📁 Directory Structure

```
src/ai_platform/
├── core/                          # Core infrastructure
│   ├── agent.py                   # BaseAgent, MicroAgent classes
│   ├── context.py                 # ContextManager for state management
│   ├── execution_log.py           # Execution logging system
│   ├── session.py                 # SessionManager with workspace control
│   ├── skills.py                  # Skill base classes
│   ├── task.py                    # Task base class and registry
│   └── __init__.py               # Core exports
│
├── agents/                        # Agent implementations
│   ├── concrete_agents.py         # Concrete agent classes
│   │   ├── CustomerAnalysisAgent
│   │   ├── GrowthOperationsAgent
│   │   └── RecommendationAgent
│   └── orchestrator.py           # (future) Main orchestrator agent
│
├── skills/                        # Skill implementations
│   ├── concrete_skills.py         # Skill implementations
│   │   ├── SunCultureDataSkill
│   │   ├── SunCultureVisualizationSkill
│   │   ├── SunCultureReportSkill
│   │   └── SunCultureAnalysisSkill
│   └── __init__.py
│
├── tasks/                         # Task implementations
│   ├── concrete_tasks.py          # Task implementations
│   │   ├── CustomerSegmentationTask
│   │   ├── GrowthPlanningTask
│   │   └── QuickInsightTask
│   └── __init__.py
│
├── config/                        # Configuration
│   ├── prompts.py                 # Prompt registry
│   ├── agents.py                  # Agent definitions
│   ├── tasks.py                   # Task definitions
│   └── __init__.py
│
├── providers/                     # LLM providers (existing)
├── api/                          # API layer (existing)
├── config.py                     # Main config
└── __init__.py
```

## 🔄 Execution Flow

### Task Workflow Example

```
User Request: "Analyze customer churn"
    ↓
[Intent Classification] → "churn_analysis" task
    ↓
[Phase 1] Plan Generation
    - Step 1: data_gathering
    - Step 2: risk_assessment
    - Step 3: recommendations
    ↓
[Phase 2] Context Gathering
    - Load customer data
    - Set metadata (analysis type, date range, etc.)
    ↓
[Phase 3] Micro-Agent Execution (parallel)
    - CustomerAnalysisAgent: fetch data → analyze → LLM insights
    - RecommendationAgent: synthesize → generate recommendations
    ↓
[Phase 4] Finalization
    - Assemble report from sections
    - Save artifacts, logs, metadata
    - Return output
    ↓
Output: Markdown report + execution log + context state
```

## 🎯 Key Patterns Applied

### 1. Provider Abstraction
```python
agent = BaseAgent(
    name="analysis_agent",
    provider="openai",  # or "gemini", "ollama", "claude"
    model="gpt-4o-mini"
)
```

### 2. Skill Composition
```python
agent.register_skill("data", DataSkill())
agent.register_skill("analysis", AnalysisSkill())
data = agent.get_skill("data").execute(...)
```

### 3. Task Registration & Discovery
```python
@Task.register("customer_segmentation")
class CustomerSegmentationTask(Task):
    ...

task = Task.get_task("customer_segmentation", session_manager=sm)
```

### 4. Execution Logging
```python
exec_log.log_data_input(source="parquet", name="customers", row_count=1000)
exec_log.log_transformation(
    input="raw", output="normalized",
    method="fillna", rows_in=1000, rows_out=999
)
exec_log.log_llm_interaction(
    agent="CustomerAnalysis", prompt=..., response=..., model="gpt-4o-mini"
)
```

### 5. Context Management
```python
ctx.set_metadata(customer_segment="enterprise")
ctx.add_section("analysis", content, artifacts=["/path/to/chart.png"])
ctx.log_llm_interaction(agent_name, prompt, response)
summary = ctx.get_summary()  # For micro-agents
```

## 🚀 Usage Examples

### Example 1: Run Customer Segmentation Task

```python
from src.ai_platform.core.session import SessionManager
from src.ai_platform.core.task import Task
from pathlib import Path

# Initialize session
workspace = Path("workspace/ai_sessions")
session_mgr = SessionManager(workspace)

# Get and execute task
task = Task.get_task(
    "customer_segmentation",
    session_manager=session_mgr
)

# Run task
result = await task.execute_workflow({
    "data_source": "parquet",
    "file_path": "data/processed/customers.parquet"
})

print(f"Report saved to: {result['report_path']}")
print(f"Execution log: {task.session_id}/execution_log.json")
```

### Example 2: Custom Agent with Skills

```python
from src.ai_platform.core.agent import MicroAgent
from src.ai_platform.skills.concrete_skills import SunCultureDataSkill, SunCultureAnalysisSkill

class CustomAgent(MicroAgent):
    def __init__(self, ...):
        super().__init__(...)
        self.register_skill("data", SunCultureDataSkill())
        self.register_skill("analysis", SunCultureAnalysisSkill())
    
    async def _perform_task(self, input_data, **kwargs):
        data = self.get_skill("data").execute(input_data)
        analysis = self.get_skill("analysis").execute(data, analysis_type="descriptive")
        insights = await self.call_llm("Analyze this data...")
        return {"analysis": analysis, "insights": insights}
```

### Example 3: Custom Task Definition

```python
from src.ai_platform.core.task import Task

@Task.register("my_custom_task")
class MyCustomTask(Task):
    def __init__(self, session_manager, session_id=None):
        super().__init__("my_custom_task", session_manager, session_id)
        # Register agents, build plan
    
    async def _gather_context(self, input_data):
        # Phase 2: Gather data
        return {...}
    
    async def _finalize(self, input_data):
        # Phase 4: Generate output
        return {...}
```

## 📊 Configuration

### Prompts Registry
```python
# config/prompts.py - maps (agent, task) → prompt template
get_prompt("customer_analysis", "segment_analysis", context="...")
```

### Agents Registry
```python
# config/agents.py - agent definitions
{
    "customer_analysis": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "capabilities": [...],
        "skills": [...]
    }
}
```

### Tasks Registry
```python
# config/tasks.py - task definitions
{
    "customer_segmentation": {
        "primary_agent": "customer_analysis",
        "micro_agents": [...],
        "phases": [...]
    }
}
```

## 🔐 Audit & Compliance

All operations are tracked:
- **execution_log.json** - complete audit trail
  - Data inputs with metadata
  - Transformations with parameters
  - LLM interactions (prompts, responses, models, latency)
  - Plan execution status
  - Errors and warnings
- **context.json** - task state
- **progress.md** - human-readable progress log
- **transcript.jsonl** - conversation history

## 🔄 Data Flow

```
User Input
    ↓
[Intent Classification] (IntentClassificationSkill)
    ↓
[Task Routing] (TaskRegistry)
    ↓
[Session Creation] (SessionManager)
    - Creates UUID folder
    - Initializes execution_log
    - Initializes context_manager
    ↓
[Micro-Agent Execution] (Task coordinates agents)
    - Phase 2: DataSkill fetches data
    - DataSkill logs data input
    - AnalysisSkill performs analysis
    - AnalysisSkill logs transformations
    - Call LLM through provider abstraction
    - LLMService logs interaction
    ↓
[Report Assembly] (ReportSkill)
    - Assemble sections from narrative
    - Add metadata
    ↓
[Output] (SessionManager)
    - Save report to reports/
    - Save artifacts to artifacts/
    - Finalize execution log
```

## 🎓 Learning Resources

Study these files to understand the architecture:
1. **core/session.py** - Session and workspace management
2. **core/execution_log.py** - Audit trail tracking
3. **core/agent.py** - Agent base classes and provider abstraction
4. **core/task.py** - Task system and orchestration
5. **skills/concrete_skills.py** - Skill implementations
6. **agents/concrete_agents.py** - Agent implementations
7. **tasks/concrete_tasks.py** - Task implementations
