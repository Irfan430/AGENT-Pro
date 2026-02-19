"""
Task State Engine - Manages persistent task state with checkpoint and recovery capabilities.
Implements state persistence, task tracking, and recovery mechanisms.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    RESUMED = "resumed"


class StepStatus(str, Enum):
    """Step execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskStep:
    """Represents a single step in task execution."""
    step_id: int
    description: str
    status: StepStatus = StepStatus.PENDING
    output: str = ""
    error: Optional[str] = None
    duration: float = 0.0
    dependencies: List[int] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskState:
    """Represents the complete state of a task."""
    task_id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Task execution details
    steps: List[TaskStep] = field(default_factory=list)
    current_step_id: int = 0
    completed_step_ids: List[int] = field(default_factory=list)
    failed_step_ids: List[int] = field(default_factory=list)
    
    # Context and memory
    working_memory: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    total_duration: float = 0.0
    token_count: int = 0
    continuation_count: int = 0
    last_checkpoint_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskStateEngine:
    """
    Manages task state with persistence and recovery capabilities.
    Tracks task execution, manages steps, and handles state transitions.
    """
    
    def __init__(self):
        """Initialize the task state engine."""
        self.tasks: Dict[str, TaskState] = {}
        self.task_history: Dict[str, List[TaskState]] = {}
        
        logger.info("Task State Engine initialized")
    
    def create_task(
        self,
        goal: str,
        steps: Optional[List[str]] = None,
    ) -> TaskState:
        """
        Create a new task.
        
        Args:
            goal: Task goal/description
            steps: Optional list of step descriptions
        
        Returns:
            Created TaskState
        """
        task_id = str(uuid.uuid4())
        
        # Create steps
        task_steps = []
        if steps:
            for idx, step_desc in enumerate(steps):
                task_steps.append(TaskStep(
                    step_id=idx,
                    description=step_desc,
                ))
        
        task_state = TaskState(
            task_id=task_id,
            goal=goal,
            steps=task_steps,
        )
        
        self.tasks[task_id] = task_state
        self.task_history[task_id] = [task_state]
        
        logger.info(f"Task created: {task_id} - {goal}")
        
        return task_state
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
    ) -> bool:
        """Update task status."""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return False
        
        task.status = status
        task.updated_at = datetime.now().isoformat()
        
        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now().isoformat()
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now().isoformat()
        
        self._save_state_history(task_id, task)
        logger.info(f"Task {task_id} status updated to {status}")
        
        return True
    
    def start_step(
        self,
        task_id: str,
        step_id: int,
    ) -> bool:
        """Mark a step as in progress."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        step = self._get_step(task, step_id)
        if not step:
            return False
        
        step.status = StepStatus.IN_PROGRESS
        task.current_step_id = step_id
        task.updated_at = datetime.now().isoformat()
        
        self._save_state_history(task_id, task)
        logger.info(f"Step {step_id} started for task {task_id}")
        
        return True
    
    def complete_step(
        self,
        task_id: str,
        step_id: int,
        output: str = "",
        duration: float = 0.0,
    ) -> bool:
        """Mark a step as completed."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        step = self._get_step(task, step_id)
        if not step:
            return False
        
        step.status = StepStatus.COMPLETED
        step.output = output
        step.duration = duration
        
        if step_id not in task.completed_step_ids:
            task.completed_step_ids.append(step_id)
        
        task.total_duration += duration
        task.updated_at = datetime.now().isoformat()
        
        self._save_state_history(task_id, task)
        logger.info(f"Step {step_id} completed for task {task_id} ({duration:.2f}s)")
        
        return True
    
    def fail_step(
        self,
        task_id: str,
        step_id: int,
        error: str,
    ) -> bool:
        """Mark a step as failed."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        step = self._get_step(task, step_id)
        if not step:
            return False
        
        step.status = StepStatus.FAILED
        step.error = error
        step.retry_count += 1
        
        if step_id not in task.failed_step_ids:
            task.failed_step_ids.append(step_id)
        
        task.updated_at = datetime.now().isoformat()
        
        self._save_state_history(task_id, task)
        logger.error(f"Step {step_id} failed for task {task_id}: {error}")
        
        return True
    
    def retry_step(self, task_id: str, step_id: int) -> bool:
        """Retry a failed step."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        step = self._get_step(task, step_id)
        if not step:
            return False
        
        if step.retry_count >= step.max_retries:
            logger.warning(f"Max retries reached for step {step_id}")
            return False
        
        step.status = StepStatus.PENDING
        step.error = None
        task.updated_at = datetime.now().isoformat()
        
        self._save_state_history(task_id, task)
        logger.info(f"Step {step_id} retried (attempt {step.retry_count + 1})")
        
        return True
    
    def update_working_memory(
        self,
        task_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """Update working memory for a task."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.working_memory[key] = value
        task.updated_at = datetime.now().isoformat()
        
        return True
    
    def get_working_memory(self, task_id: str) -> Dict[str, Any]:
        """Get working memory for a task."""
        task = self.get_task(task_id)
        return task.working_memory if task else {}
    
    def update_context(
        self,
        task_id: str,
        context: Dict[str, Any],
    ) -> bool:
        """Update task context."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.context.update(context)
        task.updated_at = datetime.now().isoformat()
        
        return True
    
    def get_pending_steps(self, task_id: str) -> List[TaskStep]:
        """Get all pending steps for a task."""
        task = self.get_task(task_id)
        if not task:
            return []
        
        return [
            step for step in task.steps
            if step.status == StepStatus.PENDING
        ]
    
    def get_next_executable_step(self, task_id: str) -> Optional[TaskStep]:
        """Get the next step that can be executed (dependencies satisfied)."""
        task = self.get_task(task_id)
        if not task:
            return None
        
        for step in task.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            # Check if dependencies are satisfied
            dependencies_met = all(
                dep_id in task.completed_step_ids
                for dep_id in step.dependencies
            )
            
            if dependencies_met:
                return step
        
        return None
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """Get task progress information."""
        task = self.get_task(task_id)
        if not task:
            return {}
        
        total_steps = len(task.steps)
        completed_steps = len(task.completed_step_ids)
        failed_steps = len(task.failed_step_ids)
        pending_steps = total_steps - completed_steps - failed_steps
        
        progress_percent = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "pending_steps": pending_steps,
            "progress_percent": progress_percent,
            "total_duration": task.total_duration,
            "continuation_count": task.continuation_count,
        }
    
    def export_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Export task state as dictionary."""
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "goal": task.goal,
            "status": task.status.value,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "steps": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "status": step.status.value,
                    "output": step.output,
                    "error": step.error,
                    "duration": step.duration,
                    "retry_count": step.retry_count,
                }
                for step in task.steps
            ],
            "working_memory": task.working_memory,
            "context": task.context,
            "progress": self.get_task_progress(task_id),
        }
    
    def _get_step(self, task: TaskState, step_id: int) -> Optional[TaskStep]:
        """Get a step by ID from task."""
        for step in task.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _save_state_history(self, task_id: str, task_state: TaskState):
        """Save task state to history."""
        if task_id not in self.task_history:
            self.task_history[task_id] = []
        
        # Create a copy for history
        import copy
        self.task_history[task_id].append(copy.deepcopy(task_state))
        
        # Keep only last 50 states
        if len(self.task_history[task_id]) > 50:
            self.task_history[task_id] = self.task_history[task_id][-50:]
    
    def get_task_history(self, task_id: str) -> List[TaskState]:
        """Get execution history for a task."""
        return self.task_history.get(task_id, [])


# Global task state engine instance
task_state_engine = TaskStateEngine()
