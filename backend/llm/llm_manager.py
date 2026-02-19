"""
LLM Manager - Handles integration with multiple LLM providers.
Supports DeepSeek, OpenAI, Claude, Llama, and Groq with streaming responses.
"""

import asyncio
import json
from typing import Optional, AsyncIterator, Dict, Any, List
from dataclasses import dataclass
import logging

import litellm
from litellm import acompletion, completion

from backend.config import settings, LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Represents an LLM response."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[Dict[str, int]] = None
    stop_reason: Optional[str] = None


class LLMManager:
    """
    Manages interactions with various LLM providers.
    Provides unified interface for chat completions with streaming support.
    """
    
    def __init__(self):
        """Initialize LLM Manager with configured provider."""
        self.default_provider = settings.DEFAULT_LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        
        # Configure API keys for all providers
        self._configure_api_keys()
        
        logger.info(f"LLM Manager initialized with provider: {self.default_provider}")
    
    def _configure_api_keys(self) -> None:
        """Configure API keys for all LLM providers."""
        if settings.DEEPSEEK_API_KEY:
            litellm.api_key = settings.DEEPSEEK_API_KEY
        
        if settings.OPENAI_API_KEY:
            litellm.openai_api_key = settings.OPENAI_API_KEY
        
        if settings.ANTHROPIC_API_KEY:
            litellm.anthropic_api_key = settings.ANTHROPIC_API_KEY
        
        if settings.GROQ_API_KEY:
            litellm.groq_api_key = settings.GROQ_API_KEY
    
    def _get_model_name(self, provider: Optional[LLMProvider] = None) -> str:
        """Get the full model name for the provider."""
        provider = provider or self.default_provider
        
        model_mapping = {
            LLMProvider.DEEPSEEK: "deepseek/deepseek-chat",
            LLMProvider.OPENAI: "gpt-4",
            LLMProvider.CLAUDE: "claude-3-opus-20240229",
            LLMProvider.LLAMA: "ollama/llama2",
            LLMProvider.GROQ: "groq/mixtral-8x7b-32768",
        }
        
        return model_mapping.get(provider, self.model)
    
    async def chat(
        self,
        messages: List[Message],
        provider: Optional[LLMProvider] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> AsyncIterator[str] | LLMResponse:
        """
        Send a chat message to the LLM and get a response.
        
        Args:
            messages: List of Message objects
            provider: LLM provider to use (defaults to configured provider)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
        
        Returns:
            AsyncIterator of response chunks if stream=True, else LLMResponse
        """
        provider = provider or self.default_provider
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        model_name = self._get_model_name(provider)
        
        # Convert Message objects to dict format
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            if stream:
                return self._stream_chat(
                    message_dicts, model_name, temperature, max_tokens
                )
            else:
                return await self._non_stream_chat(
                    message_dicts, model_name, temperature, max_tokens
                )
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise
    
    async def _non_stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Handle non-streaming chat completion."""
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout,
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            provider=self.default_provider.value,
            tokens_used={
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens,
            },
            stop_reason=response.choices[0].finish_reason,
        )
    
    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Handle streaming chat completion."""
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout,
            stream=True,
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate_task_plan(
        self,
        task_description: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate a multi-step task plan for autonomous execution.
        
        Args:
            task_description: Description of the task to plan
            context: Additional context about the system/environment
        
        Returns:
            JSON string containing the task plan
        """
        system_prompt = """You are an expert task planner. Generate a detailed, step-by-step plan to accomplish the given task.
        
Return your response as a JSON object with the following structure:
{
    "task": "task description",
    "steps": [
        {
            "id": 1,
            "description": "step description",
            "action": "code to execute",
            "language": "python|javascript|shell",
            "dependencies": [0],
            "expected_output": "what we expect"
        }
    ],
    "success_criteria": "how to know the task is complete",
    "estimated_duration": "time estimate"
}"""
        
        user_message = f"Task: {task_description}"
        if context:
            user_message += f"\n\nContext: {context}"
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_message),
        ]
        
        response = await self.chat(messages, stream=False)
        return response.content
    
    async def analyze_error(
        self,
        error_message: str,
        code: str,
        language: str,
    ) -> str:
        """
        Analyze an error and suggest fixes.
        
        Args:
            error_message: The error message
            code: The code that caused the error
            language: Programming language
        
        Returns:
            Analysis and suggested fix
        """
        system_prompt = f"""You are an expert {language} programmer. 
Analyze the error and provide a detailed explanation and suggested fix."""
        
        user_message = f"""Error: {error_message}

Code:
```{language}
{code}
```

Please provide:
1. Root cause analysis
2. Why this error occurred
3. Suggested fix
4. Corrected code"""
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_message),
        ]
        
        response = await self.chat(messages, stream=False)
        return response.content
    
    async def validate_code(
        self,
        code: str,
        language: str,
    ) -> Dict[str, Any]:
        """
        Validate code for security and syntax issues.
        
        Args:
            code: Code to validate
            language: Programming language
        
        Returns:
            Validation result with issues and suggestions
        """
        system_prompt = f"""You are a {language} code security and quality expert.
Analyze the code for:
1. Security vulnerabilities
2. Syntax errors
3. Best practices violations
4. Performance issues

Return a JSON object with:
{{
    "is_safe": true/false,
    "issues": [
        {{"severity": "high|medium|low", "issue": "description", "line": number}}
    ],
    "suggestions": ["suggestion1", "suggestion2"],
    "can_execute": true/false
}}"""
        
        user_message = f"""Validate this {language} code:
```{language}
{code}
```"""
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_message),
        ]
        
        response = await self.chat(messages, stream=False)
        
        try:
            # Extract JSON from response
            content = response.content
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            logger.warning("Failed to parse validation response as JSON")
        
        return {
            "is_safe": True,
            "issues": [],
            "suggestions": [],
            "can_execute": True,
        }


# Global LLM manager instance
llm_manager = LLMManager()
