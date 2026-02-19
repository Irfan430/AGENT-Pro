"""
Continuation Manager - Handles intelligent auto-continuation when LLM token limit is reached.
Implements checkpoint system, context compression, and automatic task resumption.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class TaskCheckpoint:
    """Represents a saved checkpoint of task execution state."""
    checkpoint_id: str
    task_id: str
    goal: str
    current_step: int
    completed_steps: List[int]
    pending_steps: List[int]
    working_memory: Dict[str, Any]
    last_llm_response: str
    tool_outputs: Dict[str, Any]
    timestamp: str
    token_count: int
    continuation_count: int = 0
    context_summary: str = ""


@dataclass
class ContinuationState:
    """State information for continuation."""
    is_truncated: bool
    finish_reason: str
    token_limit_reached: bool
    incomplete_output: bool
    last_checkpoint: Optional[TaskCheckpoint] = None


class ContinuationManager:
    """
    Manages intelligent auto-continuation for long-running tasks.
    Detects token limits, saves checkpoints, and resumes execution.
    """
    
    def __init__(self, max_continuation_attempts: int = 5):
        """
        Initialize the continuation manager.
        
        Args:
            max_continuation_attempts: Maximum number of continuation cycles
        """
        self.max_continuation_attempts = max_continuation_attempts
        self.checkpoints: Dict[str, TaskCheckpoint] = {}
        self.task_states: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Continuation Manager initialized (max attempts: {max_continuation_attempts})")
    
    def detect_token_limit(
        self,
        llm_response: Dict[str, Any],
        response_text: str,
    ) -> ContinuationState:
        """
        Detect if token limit was reached during LLM response.
        
        Args:
            llm_response: Raw LLM response object
            response_text: Generated response text
        
        Returns:
            ContinuationState with detection results
        """
        finish_reason = llm_response.get("choices", [{}])[0].get("finish_reason", "stop")
        is_truncated = finish_reason == "length"
        
        # Check for incomplete structured outputs
        incomplete_json = self._detect_incomplete_json(response_text)
        incomplete_code = self._detect_incomplete_code(response_text)
        incomplete_tool_call = self._detect_incomplete_tool_call(response_text)
        
        token_limit_reached = is_truncated or incomplete_json or incomplete_code
        incomplete_output = incomplete_json or incomplete_code or incomplete_tool_call
        
        state = ContinuationState(
            is_truncated=is_truncated,
            finish_reason=finish_reason,
            token_limit_reached=token_limit_reached,
            incomplete_output=incomplete_output,
        )
        
        if token_limit_reached:
            logger.warning(f"Token limit detected: {finish_reason}")
            logger.warning(f"Incomplete JSON: {incomplete_json}, Code: {incomplete_code}")
        
        return state
    
    def _detect_incomplete_json(self, text: str) -> bool:
        """Detect incomplete JSON in response."""
        try:
            # Check if text contains JSON-like structure
            if "{" in text and "}" not in text[-10:]:
                return True
            
            # Try to parse JSON
            json.loads(text)
            return False
        except (json.JSONDecodeError, ValueError):
            # Check if it looks like incomplete JSON
            open_braces = text.count("{")
            close_braces = text.count("}")
            return open_braces > close_braces
    
    def _detect_incomplete_code(self, text: str) -> bool:
        """Detect incomplete code blocks."""
        # Check for unclosed code blocks
        code_blocks = text.count("```")
        if code_blocks % 2 != 0:
            return True
        
        # Check for unclosed brackets/parentheses
        unclosed_patterns = [
            (text.count("("), text.count(")")),
            (text.count("["), text.count("]")),
            (text.count("{"), text.count("}")),
        ]
        
        for open_count, close_count in unclosed_patterns:
            if open_count > close_count:
                return True
        
        return False
    
    def _detect_incomplete_tool_call(self, text: str) -> bool:
        """Detect incomplete tool calls."""
        # Check for unfinished function calls
        if text.count("function_call(") > text.count(")"):
            return True
        
        # Check for incomplete XML-like tool calls
        if "<tool_call>" in text and "</tool_call>" not in text:
            return True
        
        return False
    
    def create_checkpoint(
        self,
        task_id: str,
        goal: str,
        current_step: int,
        completed_steps: List[int],
        pending_steps: List[int],
        working_memory: Dict[str, Any],
        last_llm_response: str,
        tool_outputs: Dict[str, Any],
        token_count: int,
    ) -> TaskCheckpoint:
        """
        Create and save a checkpoint of current task state.
        
        Args:
            task_id: Unique task identifier
            goal: Task goal/description
            current_step: Current step number
            completed_steps: List of completed step IDs
            pending_steps: List of pending step IDs
            working_memory: Current working memory state
            last_llm_response: Last LLM response text
            tool_outputs: Outputs from executed tools
            token_count: Current token count
        
        Returns:
            Created TaskCheckpoint
        """
        checkpoint_id = self._generate_checkpoint_id(task_id)
        
        # Compress context
        context_summary = self._compress_context(
            working_memory,
            last_llm_response,
            completed_steps,
        )
        
        checkpoint = TaskCheckpoint(
            checkpoint_id=checkpoint_id,
            task_id=task_id,
            goal=goal,
            current_step=current_step,
            completed_steps=completed_steps,
            pending_steps=pending_steps,
            working_memory=working_memory,
            last_llm_response=last_llm_response,
            tool_outputs=tool_outputs,
            timestamp=datetime.now().isoformat(),
            token_count=token_count,
            context_summary=context_summary,
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        logger.info(f"Checkpoint created: {checkpoint_id} for task {task_id}")
        
        return checkpoint
    
    def _generate_checkpoint_id(self, task_id: str) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().isoformat()
        combined = f"{task_id}_{timestamp}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"ckpt_{hash_val}"
    
    def _compress_context(
        self,
        working_memory: Dict[str, Any],
        last_response: str,
        completed_steps: List[int],
    ) -> str:
        """
        Compress context for memory efficiency.
        
        Args:
            working_memory: Current working memory
            last_response: Last LLM response
            completed_steps: Completed steps
        
        Returns:
            Compressed context summary
        """
        summary_parts = []
        
        # Summarize completed steps
        if completed_steps:
            summary_parts.append(f"Completed {len(completed_steps)} steps: {completed_steps}")
        
        # Extract key information from working memory
        if isinstance(working_memory, dict):
            for key, value in working_memory.items():
                if isinstance(value, (str, int, float, bool)):
                    summary_parts.append(f"{key}: {value}")
        
        # Summarize last response (first 200 chars)
        if last_response:
            summary_parts.append(f"Last response: {last_response[:200]}...")
        
        return " | ".join(summary_parts)
    
    def resume_from_checkpoint(
        self,
        checkpoint_id: str,
    ) -> Optional[TaskCheckpoint]:
        """
        Resume task execution from a saved checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to resume from
        
        Returns:
            TaskCheckpoint if found, None otherwise
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        
        if not checkpoint:
            logger.error(f"Checkpoint not found: {checkpoint_id}")
            return None
        
        logger.info(f"Resuming from checkpoint: {checkpoint_id}")
        return checkpoint
    
    def get_continuation_prompt(
        self,
        checkpoint: TaskCheckpoint,
        incomplete_output: str,
    ) -> str:
        """
        Generate a prompt for continuing from checkpoint.
        
        Args:
            checkpoint: Checkpoint to resume from
            incomplete_output: Incomplete output to continue from
        
        Returns:
            Continuation prompt
        """
        prompt = f"""
You are resuming a task that was interrupted due to token limit.

TASK GOAL: {checkpoint.goal}

PROGRESS:
- Current Step: {checkpoint.current_step}
- Completed Steps: {checkpoint.completed_steps}
- Pending Steps: {checkpoint.pending_steps}

CONTEXT SUMMARY:
{checkpoint.context_summary}

LAST INCOMPLETE OUTPUT:
{incomplete_output}

INSTRUCTIONS:
1. Continue from where the previous response was cut off
2. Complete the current step
3. Move to the next pending step
4. Maintain consistency with previous outputs
5. Use the provided context to understand the task state

Continue now:
"""
        return prompt.strip()
    
    def should_continue(
        self,
        task_id: str,
        continuation_count: int,
    ) -> bool:
        """
        Determine if task should continue or stop.
        
        Args:
            task_id: Task identifier
            continuation_count: Number of continuations so far
        
        Returns:
            True if should continue, False if should stop
        """
        if continuation_count >= self.max_continuation_attempts:
            logger.warning(f"Max continuation attempts reached for task {task_id}")
            return False
        
        return True
    
    def detect_infinite_loop(
        self,
        task_id: str,
        last_responses: List[str],
    ) -> bool:
        """
        Detect if task is stuck in an infinite loop.
        
        Args:
            task_id: Task identifier
            last_responses: List of last N responses
        
        Returns:
            True if infinite loop detected, False otherwise
        """
        if len(last_responses) < 3:
            return False
        
        # Check if last 3 responses are identical
        if len(set(last_responses[-3:])) == 1:
            logger.warning(f"Infinite loop detected for task {task_id}")
            return True
        
        # Check for high similarity
        similarity_threshold = 0.95
        if self._calculate_similarity(last_responses[-2], last_responses[-1]) > similarity_threshold:
            logger.warning(f"High similarity detected in consecutive responses for task {task_id}")
            return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)."""
        if not text1 or not text2:
            return 0.0
        
        # Simple similarity based on common words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        common = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return common / total if total > 0 else 0.0
    
    def cleanup_old_checkpoints(self, keep_last_n: int = 5):
        """Remove old checkpoints, keeping only the last N."""
        if len(self.checkpoints) > keep_last_n:
            # Sort by timestamp and remove oldest
            sorted_checkpoints = sorted(
                self.checkpoints.items(),
                key=lambda x: x[1].timestamp,
            )
            
            for checkpoint_id, _ in sorted_checkpoints[:-keep_last_n]:
                del self.checkpoints[checkpoint_id]
                logger.info(f"Removed old checkpoint: {checkpoint_id}")


# Global continuation manager instance
continuation_manager = ContinuationManager()
