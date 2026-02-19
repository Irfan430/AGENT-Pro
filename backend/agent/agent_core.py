"""
Agent Core - Main agent logic for autonomous task execution.
Handles task planning, execution, self-healing, and workflow management.
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any, AsyncIterator
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

from backend.config import settings
from backend.llm.llm_manager import llm_manager, Message
from backend.executor.code_executor import code_executor

logger = logging.getLogger(__name__)


@dataclass
class TaskStep:
    """Represents a single step in a task plan."""
    id: int
    description: str
    action: str
    language: str
    dependencies: List[int] = field(default_factory=list)
    expected_output: str = ""
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TaskPlan:
    """Represents a complete task plan."""
    task_id: str
    task_description: str
    steps: List[TaskStep] = field(default_factory=list)
    success_criteria: str = ""
    estimated_duration: float = 0.0
    status: str = "created"  # created, executing, completed, failed
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["steps"] = [step.to_dict() for step in self.steps]
        return data


@dataclass
class ConversationMessage:
    """Represents a message in the conversation history."""
    role: str  # "user", "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_id: Optional[str] = None
    code_blocks: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AutonomousAgent:
    """
    Main autonomous agent that handles task execution.
    Manages conversation history, task planning, and self-healing execution.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the autonomous agent.
        
        Args:
            session_id: Optional session ID for resuming conversations
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.conversation_history: List[ConversationMessage] = []
        self.current_plan: Optional[TaskPlan] = None
        self.execution_history: List[Dict[str, Any]] = []
        self.system_message = self._get_system_message()
        
        logger.info(f"Agent initialized with session_id: {self.session_id}")
    
    def _get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """You are an autonomous AI agent with complete control over the user's device.
Your capabilities include:
- Executing code in Python, JavaScript, Shell, Java, R, and Ruby
- Creating and editing files
- Analyzing data and generating visualizations
- Controlling the browser for web automation
- Managing system tasks and processes
- Analyzing images and screenshots
- Generating diagrams and flowcharts

Always:
1. Break complex tasks into smaller steps
2. Validate code before execution
3. Handle errors gracefully with self-healing logic
4. Provide clear explanations of what you're doing
5. Ask for clarification if the task is ambiguous
6. Respect safety constraints and user preferences

When executing code:
- Always provide the code in a code block with the language specified
- Explain what the code does before executing it
- If execution fails, analyze the error and suggest fixes
- Use self-healing logic to automatically retry with corrections"""
    
    async def chat(
        self,
        user_message: str,
        stream: bool = False,
        auto_execute: bool = False,
    ) -> AsyncIterator[str] | str:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's message
            stream: Whether to stream the response
            auto_execute: Whether to automatically execute code
        
        Returns:
            Response text or async iterator of response chunks
        """
        # Add user message to history
        self.conversation_history.append(
            ConversationMessage(role="user", content=user_message)
        )
        
        # Prepare messages for LLM
        messages = [Message(role="system", content=self.system_message)]
        
        for msg in self.conversation_history:
            messages.append(Message(role=msg.role, content=msg.content))
        
        try:
            if stream:
                return self._stream_response(messages, user_message, auto_execute)
            else:
                response = await llm_manager.chat(messages, stream=False)
                
                # Add assistant response to history
                self.conversation_history.append(
                    ConversationMessage(role="assistant", content=response.content)
                )
                
                # Auto-execute code if requested
                if auto_execute:
                    await self._auto_execute_code(response.content)
                
                return response.content
        
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            error_message = f"Error processing request: {str(e)}"
            self.conversation_history.append(
                ConversationMessage(role="assistant", content=error_message)
            )
            return error_message
    
    async def _stream_response(
        self,
        messages: List[Message],
        user_message: str,
        auto_execute: bool,
    ) -> AsyncIterator[str]:
        """Stream response from LLM."""
        full_response = ""
        
        async for chunk in await llm_manager.chat(messages, stream=True):
            full_response += chunk
            yield chunk
        
        # Add to history after streaming completes
        self.conversation_history.append(
            ConversationMessage(role="assistant", content=full_response)
        )
        
        # Auto-execute code if requested
        if auto_execute:
            await self._auto_execute_code(full_response)
    
    async def _auto_execute_code(self, response_text: str) -> None:
        """
        Extract and execute code from the response.
        
        Args:
            response_text: The response text containing code blocks
        """
        # Extract code blocks from response
        code_blocks = self._extract_code_blocks(response_text)
        
        for code_block in code_blocks:
            language = code_block.get("language", "python")
            code = code_block.get("code", "")
            
            if not code.strip():
                continue
            
            logger.info(f"Auto-executing {language} code")
            
            # Validate code
            is_valid, error = code_executor.validate_code_syntax(code, language)
            if not is_valid:
                logger.warning(f"Code validation failed: {error}")
                continue
            
            # Execute code
            result = await code_executor.execute(code, language)
            
            # Store execution result
            self.execution_history.append(result.to_dict())
            
            if not result.success:
                logger.error(f"Code execution failed: {result.error}")
    
    async def create_task_plan(
        self,
        task_description: str,
        context: Optional[str] = None,
    ) -> TaskPlan:
        """
        Create a multi-step task plan for autonomous execution.
        
        Args:
            task_description: Description of the task
            context: Additional context
        
        Returns:
            TaskPlan with steps
        """
        logger.info(f"Creating task plan for: {task_description}")
        
        # Generate plan using LLM
        plan_json = await llm_manager.generate_task_plan(task_description, context)
        
        try:
            plan_data = json.loads(plan_json)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = plan_json.find("{")
            end = plan_json.rfind("}") + 1
            if start != -1 and end > start:
                plan_data = json.loads(plan_json[start:end])
            else:
                raise ValueError("Failed to parse task plan")
        
        # Create TaskPlan object
        task_id = str(uuid.uuid4())
        plan = TaskPlan(
            task_id=task_id,
            task_description=task_description,
            success_criteria=plan_data.get("success_criteria", ""),
            estimated_duration=plan_data.get("estimated_duration", 0),
        )
        
        # Add steps
        for step_data in plan_data.get("steps", []):
            step = TaskStep(
                id=step_data.get("id", 0),
                description=step_data.get("description", ""),
                action=step_data.get("action", ""),
                language=step_data.get("language", "python"),
                dependencies=step_data.get("dependencies", []),
                expected_output=step_data.get("expected_output", ""),
            )
            plan.steps.append(step)
        
        self.current_plan = plan
        return plan
    
    async def execute_task_plan(
        self,
        plan: Optional[TaskPlan] = None,
        auto_heal: bool = True,
    ) -> TaskPlan:
        """
        Execute a task plan with optional self-healing.
        
        Args:
            plan: TaskPlan to execute (uses current_plan if not provided)
            auto_heal: Whether to enable self-healing on errors
        
        Returns:
            Completed TaskPlan with results
        """
        plan = plan or self.current_plan
        if not plan:
            raise ValueError("No task plan to execute")
        
        logger.info(f"Executing task plan: {plan.task_id}")
        plan.status = "executing"
        
        # Execute steps in order
        for step in plan.steps:
            # Check dependencies
            if not self._dependencies_met(step, plan):
                step.status = "skipped"
                continue
            
            step.status = "executing"
            
            # Execute step
            result = await code_executor.execute(step.action, step.language)
            
            if result.success:
                step.status = "completed"
                step.result = result.output
            else:
                step.status = "failed"
                step.error = result.error
                
                # Try self-healing if enabled
                if auto_heal:
                    logger.info(f"Attempting self-healing for step {step.id}")
                    healed_result = await self._self_heal_step(step)
                    
                    if healed_result.success:
                        step.status = "completed"
                        step.result = healed_result.output
                        step.retry_count += 1
                    else:
                        # Self-healing failed, continue to next step
                        logger.warning(f"Self-healing failed for step {step.id}")
            
            step.duration = result.duration
        
        plan.status = "completed"
        plan.completed_at = datetime.utcnow().isoformat()
        
        return plan
    
    async def _self_heal_step(self, step: TaskStep) -> Any:
        """
        Attempt to self-heal a failed step by analyzing the error and fixing the code.
        
        Args:
            step: The failed TaskStep
        
        Returns:
            ExecutionResult from retry
        """
        # Analyze error and get suggestions
        analysis = await llm_manager.analyze_error(
            step.error or "Unknown error",
            step.action,
            step.language,
        )
        
        # Extract corrected code from analysis
        corrected_code = self._extract_corrected_code(analysis, step.language)
        
        if corrected_code:
            # Retry with corrected code
            result = await code_executor.execute(corrected_code, step.language)
            step.action = corrected_code  # Update step with corrected code
            return result
        
        # Return original result if no fix found
        return await code_executor.execute(step.action, step.language)
    
    def _dependencies_met(self, step: TaskStep, plan: TaskPlan) -> bool:
        """Check if all dependencies for a step are met."""
        for dep_id in step.dependencies:
            dep_step = next((s for s in plan.steps if s.id == dep_id), None)
            if not dep_step or dep_step.status != "completed":
                return False
        return True
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from text."""
        import re
        
        code_blocks = []
        pattern = r"```(\w+)?\n(.*?)\n```"
        
        for match in re.finditer(pattern, text, re.DOTALL):
            language = match.group(1) or "python"
            code = match.group(2)
            code_blocks.append({"language": language, "code": code})
        
        return code_blocks
    
    def _extract_corrected_code(self, analysis: str, language: str) -> Optional[str]:
        """Extract corrected code from analysis text."""
        code_blocks = self._extract_code_blocks(analysis)
        
        for block in code_blocks:
            if block.get("language") == language:
                return block.get("code")
        
        return None
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return [msg.to_dict() for msg in self.conversation_history]
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the execution history."""
        return self.execution_history
    
    def clear_history(self) -> None:
        """Clear conversation and execution history."""
        self.conversation_history = []
        self.execution_history = []
        logger.info(f"History cleared for session {self.session_id}")
    
    def save_session(self) -> Dict[str, Any]:
        """Save the current session state."""
        return {
            "session_id": self.session_id,
            "conversation_history": self.get_conversation_history(),
            "execution_history": self.get_execution_history(),
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
        }
    
    def load_session(self, session_data: Dict[str, Any]) -> None:
        """Load a session from saved data."""
        self.session_id = session_data.get("session_id", self.session_id)
        
        # Restore conversation history
        for msg_data in session_data.get("conversation_history", []):
            msg = ConversationMessage(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=msg_data.get("timestamp"),
            )
            self.conversation_history.append(msg)
        
        # Restore execution history
        self.execution_history = session_data.get("execution_history", [])
        
        logger.info(f"Session loaded: {self.session_id}")


# Global agent instance (can be replaced per session)
agent = AutonomousAgent()
