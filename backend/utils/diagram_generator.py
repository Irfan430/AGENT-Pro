"""
Diagram Generator - Generates visual diagrams and flowcharts for task execution plans.
Creates Mermaid diagrams and flowcharts for visualization.
"""

import logging
import json
from typing import List, Dict, Any, Optional

from backend.agent.agent_core import TaskPlan, TaskStep

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """
    Generates diagrams and flowcharts for task plans and execution flows.
    Supports Mermaid diagram format for easy visualization.
    """
    
    def __init__(self):
        """Initialize the diagram generator."""
        logger.info("Diagram Generator initialized")
    
    def generate_task_flowchart(self, plan: TaskPlan) -> str:
        """
        Generate a Mermaid flowchart for a task plan.
        
        Args:
            plan: TaskPlan to visualize
        
        Returns:
            Mermaid diagram code
        """
        lines = ["graph TD"]
        
        # Add start node
        lines.append('    Start["Start: ' + plan.task_description.replace('"', '\\"') + '"]')
        
        # Add step nodes
        for step in plan.steps:
            node_id = f"Step{step.id}"
            label = step.description.replace('"', '\\"')
            lines.append(f'    {node_id}["{label}"]')
        
        # Add end node
        lines.append('    End["End"]')
        
        # Add connections
        prev_node = "Start"
        for step in plan.steps:
            node_id = f"Step{step.id}"
            
            if step.dependencies:
                # Connect from dependencies
                for dep_id in step.dependencies:
                    dep_node = f"Step{dep_id}"
                    lines.append(f"    {dep_node} --> {node_id}")
            else:
                # Connect from previous step
                if prev_node == "Start":
                    lines.append(f"    {prev_node} --> {node_id}")
                else:
                    lines.append(f"    {prev_node} --> {node_id}")
            
            prev_node = node_id
        
        # Connect to end
        lines.append(f"    {prev_node} --> End")
        
        return "\n".join(lines)
    
    def generate_execution_timeline(self, plan: TaskPlan) -> str:
        """
        Generate a timeline diagram for task execution.
        
        Args:
            plan: Completed TaskPlan with execution results
        
        Returns:
            Mermaid timeline code
        """
        lines = ["timeline"]
        lines.append(f'    title Task Execution Timeline: {plan.task_description}')
        
        for step in plan.steps:
            status_icon = "✓" if step.status == "completed" else "✗"
            duration = f"{step.duration:.2f}s" if step.duration else "N/A"
            
            lines.append(f'    {status_icon} Step {step.id}: {step.description} ({duration})')
        
        return "\n".join(lines)
    
    def generate_dependency_graph(self, plan: TaskPlan) -> str:
        """
        Generate a dependency graph for task steps.
        
        Args:
            plan: TaskPlan to visualize
        
        Returns:
            Mermaid graph code
        """
        lines = ["graph LR"]
        
        # Add all step nodes
        for step in plan.steps:
            node_id = f"S{step.id}"
            label = f"Step {step.id}"
            lines.append(f'    {node_id}["{label}"]')
        
        # Add dependency connections
        for step in plan.steps:
            node_id = f"S{step.id}"
            for dep_id in step.dependencies:
                dep_node = f"S{dep_id}"
                lines.append(f"    {dep_node} --> {node_id}")
        
        return "\n".join(lines)
    
    def generate_execution_summary(self, plan: TaskPlan) -> str:
        """
        Generate a summary diagram of execution results.
        
        Args:
            plan: Completed TaskPlan
        
        Returns:
            Mermaid pie chart code
        """
        completed = sum(1 for s in plan.steps if s.status == "completed")
        failed = sum(1 for s in plan.steps if s.status == "failed")
        skipped = sum(1 for s in plan.steps if s.status == "skipped")
        pending = sum(1 for s in plan.steps if s.status == "pending")
        
        lines = ["pie title Task Execution Summary"]
        
        if completed > 0:
            lines.append(f'    "Completed" : {completed}')
        if failed > 0:
            lines.append(f'    "Failed" : {failed}')
        if skipped > 0:
            lines.append(f'    "Skipped" : {skipped}')
        if pending > 0:
            lines.append(f'    "Pending" : {pending}')
        
        return "\n".join(lines)
    
    def generate_system_architecture(self) -> str:
        """
        Generate a diagram of the system architecture.
        
        Returns:
            Mermaid architecture diagram
        """
        diagram = """graph TB
    subgraph Frontend["Frontend - React GUI"]
        UI["Chat Interface"]
        CodeView["Code Preview"]
        History["Execution History"]
    end
    
    subgraph Backend["Backend - FastAPI"]
        Agent["Agent Core"]
        LLM["LLM Manager"]
        Executor["Code Executor"]
    end
    
    subgraph Services["External Services"]
        DeepSeek["DeepSeek API"]
        OpenAI["OpenAI API"]
        Whisper["Whisper API"]
    end
    
    subgraph Storage["Storage"]
        DB["Database"]
        Cache["Redis Cache"]
    end
    
    UI --> Agent
    CodeView --> Executor
    History --> DB
    Agent --> LLM
    Agent --> Executor
    LLM --> DeepSeek
    LLM --> OpenAI
    Executor --> Cache
    DB --> Cache
    Whisper -.-> Frontend
"""
        return diagram
    
    def generate_code_execution_flow(self) -> str:
        """
        Generate a diagram of the code execution flow.
        
        Returns:
            Mermaid flow diagram
        """
        diagram = """graph TD
    A["User Input"] --> B["LLM Processing"]
    B --> C{"Code Detected?"}
    C -->|No| D["Return Response"]
    C -->|Yes| E["Code Validation"]
    E --> F{"Safe?"}
    F -->|No| G["Show Warning"]
    G --> H{"User Approves?"}
    F -->|Yes| I["Execute Code"]
    H -->|No| D
    H -->|Yes| I
    I --> J{"Success?"}
    J -->|Yes| K["Return Output"]
    J -->|No| L["Self-Heal"]
    L --> M{"Fixed?"}
    M -->|Yes| K
    M -->|No| N["Return Error"]
    K --> O["Update History"]
    N --> O
    D --> O
    G --> O
"""
        return diagram
    
    def generate_html_diagram(self, mermaid_code: str) -> str:
        """
        Generate HTML for displaying a Mermaid diagram.
        
        Args:
            mermaid_code: Mermaid diagram code
        
        Returns:
            HTML string
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .diagram-container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 1200px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="diagram-container">
        <div class="mermaid">
{mermaid_code}
        </div>
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        mermaid.contentLoaded();
    </script>
</body>
</html>"""
        return html


# Global diagram generator instance
diagram_generator = DiagramGenerator()
