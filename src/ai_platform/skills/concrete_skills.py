"""Concrete skill implementations for Sunculture AI platform."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import pandas as pd

from ..core.execution_log import ExecutionLog
from ..core.skills import AnalysisSkill, DataSkill, ReportSkill, VisualizationSkill


class SunCultureDataSkill(DataSkill):
    """Data skill for fetching and transforming Sunculture data."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__(execution_log)
        self.data_sources = {}
    
    def fetch_data(self, source: str, query: Optional[Dict] = None, **kwargs) -> Any:
        """Fetch data from a source (database, file, API)."""
        input_id = ""
        
        if source == "parquet":
            # Load from parquet file
            file_path = kwargs.get("file_path")
            df = pd.read_parquet(file_path)
            
            if self.execution_log:
                input_id = self.execution_log.log_data_input(
                    source="parquet",
                    name=kwargs.get("name", file_path),
                    row_count=len(df),
                    column_count=len(df.columns),
                )
            
            return df
        
        elif source == "csv":
            # Load from CSV file
            file_path = kwargs.get("file_path")
            df = pd.read_csv(file_path)
            
            if self.execution_log:
                input_id = self.execution_log.log_data_input(
                    source="csv",
                    name=kwargs.get("name", file_path),
                    row_count=len(df),
                    column_count=len(df.columns),
                )
            
            return df
        
        elif source == "database":
            # Fetch from database (placeholder)
            raise NotImplementedError("Database source not yet implemented")
        
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def transform_data(self, data: Any, transformations: Optional[Dict] = None, **kwargs) -> Any:
        """Apply transformations to data."""
        if not isinstance(data, pd.DataFrame):
            return data
        
        df = data.copy()
        transformations = transformations or {}
        
        for transform_name, params in transformations.items():
            if transform_name == "fillna":
                df = df.fillna(params.get("value", 0))
                
                if self.execution_log:
                    self.log_transformation(
                        input_dataset="raw",
                        output_dataset=f"filled_{transform_name}",
                        method="fillna",
                        parameters=params,
                        rows_in=len(data),
                        rows_out=len(df),
                    )
            
            elif transform_name == "drop_nulls":
                subset = params.get("subset")
                df = df.dropna(subset=subset)
                
                if self.execution_log:
                    self.log_transformation(
                        input_dataset="raw",
                        output_dataset=f"dropped_nulls",
                        method="dropna",
                        parameters=params,
                        rows_in=len(data),
                        rows_out=len(df),
                    )
            
            elif transform_name == "aggregate":
                group_by = params.get("group_by", [])
                agg_dict = params.get("agg", {})
                df = df.groupby(group_by, as_index=False).agg(agg_dict)
                
                if self.execution_log:
                    self.log_transformation(
                        input_dataset="raw",
                        output_dataset="aggregated",
                        method="groupby_agg",
                        parameters=params,
                        rows_in=len(data),
                        rows_out=len(df),
                    )
        
        return df


class SunCultureVisualizationSkill(VisualizationSkill):
    """Visualization skill for generating charts and diagrams."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__(execution_log)
    
    def generate_chart(self, data: Any, chart_type: str, **kwargs) -> bytes:
        """Generate a chart as image bytes."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.style.use("seaborn-v0_8-darkgrid")
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == "line":
                x = kwargs.get("x")
                y = kwargs.get("y")
                ax.plot(data[x], data[y], marker="o")
                ax.set_xlabel(x)
                ax.set_ylabel(y)
            
            elif chart_type == "bar":
                x = kwargs.get("x")
                y = kwargs.get("y")
                data.plot(x=x, y=y, kind="bar", ax=ax)
                ax.set_xlabel(x)
                ax.set_ylabel(y)
            
            elif chart_type == "scatter":
                x = kwargs.get("x")
                y = kwargs.get("y")
                ax.scatter(data[x], data[y], alpha=0.6)
                ax.set_xlabel(x)
                ax.set_ylabel(y)
            
            elif chart_type == "histogram":
                column = kwargs.get("column")
                ax.hist(data[column], bins=20, alpha=0.7)
                ax.set_xlabel(column)
                ax.set_ylabel("Frequency")
            
            else:
                raise ValueError(f"Unknown chart type: {chart_type}")
            
            title = kwargs.get("title", chart_type.capitalize())
            ax.set_title(title, fontsize=14, fontweight="bold")
            
            # Save to bytes
            from io import BytesIO
            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
            buf.seek(0)
            chart_bytes = buf.getvalue()
            plt.close(fig)
            
            return chart_bytes
        
        except Exception as e:
            raise RuntimeError(f"Failed to generate chart: {e}")


class SunCultureReportSkill(ReportSkill):
    """Report skill for assembling markdown reports."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__(execution_log)
    
    def assemble_report(self, **kwargs) -> str:
        """Assemble sections into markdown report."""
        title = kwargs.get("title", "AI Analysis Report")
        subtitle = kwargs.get("subtitle", "")
        
        report = f"# {title}\n\n"
        
        if subtitle:
            report += f"_{subtitle}_\n\n"
        
        # Add executive summary if provided
        executive_summary = kwargs.get("executive_summary", "")
        if executive_summary:
            report += "## Executive Summary\n\n"
            report += executive_summary + "\n\n"
        
        # Add sections
        for section_title, section_content in self.sections.items():
            report += f"## {section_title}\n\n"
            report += section_content + "\n\n"
        
        # Add recommendations if provided
        recommendations = kwargs.get("recommendations", "")
        if recommendations:
            report += "## Recommendations\n\n"
            report += recommendations + "\n\n"
        
        # Add metadata
        metadata = kwargs.get("metadata", {})
        if metadata:
            report += "---\n\n"
            report += "_Report Metadata_\n\n"
            for key, value in metadata.items():
                report += f"- **{key}**: {value}\n"
        
        return report


class SunCultureAnalysisSkill(AnalysisSkill):
    """Analysis skill for statistical and business analysis."""
    
    def __init__(self, execution_log: Optional[ExecutionLog] = None):
        super().__init__(execution_log)
    
    def analyze(self, data: Any, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Perform analysis on data."""
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        results = {}
        
        if analysis_type == "descriptive":
            results["describe"] = data.describe().to_dict()
            results["nulls"] = data.isnull().sum().to_dict()
            results["dtypes"] = data.dtypes.astype(str).to_dict()
        
        elif analysis_type == "correlation":
            numeric_data = data.select_dtypes(include=["number"])
            results["correlation_matrix"] = numeric_data.corr().to_dict()
        
        elif analysis_type == "distribution":
            numeric_data = data.select_dtypes(include=["number"])
            for col in numeric_data.columns:
                results[col] = {
                    "mean": float(data[col].mean()),
                    "median": float(data[col].median()),
                    "std": float(data[col].std()),
                    "min": float(data[col].min()),
                    "max": float(data[col].max()),
                }
        
        elif analysis_type == "aggregation":
            group_by = kwargs.get("group_by", [])
            if group_by:
                results["aggregation"] = data.groupby(group_by).agg("mean").to_dict()
        
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        return results
