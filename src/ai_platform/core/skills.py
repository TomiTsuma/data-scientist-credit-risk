"""Base skill class for reusable, composable AI platform components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .execution_log import ExecutionLog


class Skill(ABC):
    """Base class for all skills - reusable, stateless components."""
    
    def __init__(self, name: str, execution_log: Optional[ExecutionLog] = None):
        self.name = name
        self.execution_log = execution_log
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the skill with given parameters."""
        pass
    
    def log_transformation(
        self,
        input_dataset: str,
        output_dataset: str,
        method: str,
        parameters: Dict[str, Any] = None,
        **additional_info,
    ) -> str:
        """Log a transformation if execution log is available."""
        if self.execution_log:
            return self.execution_log.log_transformation(
                input_dataset=input_dataset,
                output_dataset=output_dataset,
                method=method,
                parameters=parameters or {},
                **additional_info,
            )
        return ""


class DataSkill(Skill):
    """Base skill for data extraction, transformation, and normalization."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__("DataSkill", execution_log)
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> Any:
        """Fetch raw data from source."""
        pass
    
    @abstractmethod
    def transform_data(self, data: Any, **kwargs) -> Any:
        """Transform and normalize data."""
        pass
    
    def execute(self, **kwargs) -> Any:
        """Execute data pipeline: fetch → transform."""
        data = self.fetch_data(**kwargs)
        return self.transform_data(data, **kwargs)


class VisualizationSkill(Skill):
    """Base skill for generating visualizations and charts."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__("VisualizationSkill", execution_log)
    
    @abstractmethod
    def generate_chart(self, data: Any, chart_type: str, **kwargs) -> bytes:
        """Generate a chart as image bytes."""
        pass
    
    def execute(self, data: Any, chart_type: str, **kwargs) -> bytes:
        """Execute chart generation."""
        return self.generate_chart(data, chart_type, **kwargs)


class ReportSkill(Skill):
    """Base skill for assembling markdown reports and documents."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__("ReportSkill", execution_log)
        self.sections: Dict[str, str] = {}
    
    def add_section(self, title: str, content: str) -> None:
        """Add a section to the report."""
        self.sections[title] = content
    
    @abstractmethod
    def assemble_report(self, **kwargs) -> str:
        """Assemble sections into final markdown report."""
        pass
    
    def execute(self, **kwargs) -> str:
        """Execute report assembly."""
        return self.assemble_report(**kwargs)


class AnalysisSkill(Skill):
    """Base skill for performing analysis on data."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__("AnalysisSkill", execution_log)
    
    @abstractmethod
    def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Perform analysis and return results."""
        pass
    
    def execute(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Execute analysis."""
        return self.analyze(data, **kwargs)


class IntentClassificationSkill(Skill):
    """Base skill for classifying user intent and routing to appropriate task."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__("IntentClassificationSkill", execution_log)
        self.task_registry: Dict[str, str] = {}
    
    def register_task(self, intent_keyword: str, task_name: str) -> None:
        """Register a task for an intent keyword."""
        self.task_registry[intent_keyword.lower()] = task_name
    
    @abstractmethod
    def classify(self, text: str) -> Optional[str]:
        """Classify text intent and return task name."""
        pass
    
    def execute(self, text: str) -> Optional[str]:
        """Execute intent classification."""
        return self.classify(text)
