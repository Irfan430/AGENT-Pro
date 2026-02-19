"""
LLM Manager - Handles integration with multiple LLM providers.
Supports DeepSeek, OpenAI, Claude with streaming responses.
"""

import asyncio
import json
from typing import Optional, AsyncIterator, Dict, Any, List
from dataclasses import dataclass
import logging

import openai
from openai import AsyncOpenAI, OpenAI

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
        
        # Initialize API clients
        self._init_clients()
        
        logger.info(f"LLM Manager initialized with provider: {self.default_provider}")
    
    def _init_clients(self) -> None:
        """Initialize API clients for all providers."""
        # DeepSeek client
        if settings.DEEPSEEK_API_KEY:
            self.deepseek_client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
            self.deepseek_sync_client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
        
        # OpenAI client
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.openai_sync_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Anthropic client (if available)
        if settings.ANTHROPIC_API_KEY:
            try:
                from anthropic import AsyncAnthropic, Anthropic
                self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.anthropic_sync_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except ImportError:
                logger.warning("Anthropic SDK not available")
    
    def _get_model_name(self, provider: Optional[LLMProvider] = None) -> str:
        """Get the full model name for the provider."""
        provider = provider or self.default_provider
        
        model_mapping = {
            LLMProvider.DEEPSEEK: "deepseek-chat",
            LLMProvider.OPENAI: "gpt-4",
            LLMProvider.CLAUDE: "claude-3-opus-20240229",
            LLMProvider.LLAMA: "llama2",
            LLMProvider.GROQ: "mixtral-8x7b-32768",
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
                    message_dicts, model_name, temperature, max_tokens, provider
                )
            else:
                return await self._non_stream_chat(
                    message_dicts, model_name, temperature, max_tokens, provider
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
        provider: LLMProvider,
    ) -> LLMResponse:
        """Handle non-streaming chat completion."""
        try:
            if provider == LLMProvider.DEEPSEEK:
                response = await self.deepseek_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
            elif provider == LLMProvider.OPENAI:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
            else:
                # Default to DeepSeek
                response = await self.deepseek_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider=provider.value,
                tokens_used={
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                } if response.usage else None,
                stop_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logger.error(f"Error in non-stream chat: {str(e)}")
            raise
    
    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        provider: LLMProvider,
    ) -> AsyncIterator[str]:
        """Handle streaming chat completion."""
        try:
            if provider == LLMProvider.DEEPSEEK:
                stream = await self.deepseek_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    timeout=self.timeout,
                )
            elif provider == LLMProvider.OPENAI:
                stream = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    timeout=self.timeout,
                )
            else:
                stream = await self.deepseek_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    timeout=self.timeout,
                )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error in stream chat: {str(e)}")
            raise
    
    def chat_sync(
        self,
        messages: List[Message],
        provider: Optional[LLMProvider] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Synchronous chat completion (blocking)."""
        provider = provider or self.default_provider
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        model_name = self._get_model_name(provider)
        
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            if provider == LLMProvider.DEEPSEEK:
                response = self.deepseek_sync_client.chat.completions.create(
                    model=model_name,
                    messages=message_dicts,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
            elif provider == LLMProvider.OPENAI:
                response = self.openai_sync_client.chat.completions.create(
                    model=model_name,
                    messages=message_dicts,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
            else:
                response = self.deepseek_sync_client.chat.completions.create(
                    model=model_name,
                    messages=message_dicts,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=model_name,
                provider=provider.value,
                tokens_used={
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                } if response.usage else None,
                stop_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logger.error(f"Error in sync chat: {str(e)}")
            raise


# Global LLM Manager instance
llm_manager = LLMManager()
