"""
Memory Manager - Implements intelligent context compression and memory management.
Provides sliding window memory, summary memory, and hierarchical memory blocks.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class MemoryBlock:
    """Represents a block of memory."""
    block_id: str
    content: str
    summary: str
    timestamp: str
    importance_score: float
    token_count: int


class MemoryManager:
    """
    Manages memory with intelligent compression and retrieval.
    Implements sliding window, summary, and hierarchical memory strategies.
    """
    
    def __init__(
        self,
        max_memory_tokens: int = 4000,
        summary_ratio: float = 0.3,
        window_size: int = 5,
    ):
        """
        Initialize memory manager.
        
        Args:
            max_memory_tokens: Maximum tokens to keep in memory
            summary_ratio: Ratio of memory to keep as summary
            window_size: Size of sliding window
        """
        self.max_memory_tokens = max_memory_tokens
        self.summary_ratio = summary_ratio
        self.window_size = window_size
        
        self.memory_blocks: List[MemoryBlock] = []
        self.current_token_count = 0
        
        logger.info(f"Memory Manager initialized (max tokens: {max_memory_tokens})")
    
    def add_memory(
        self,
        content: str,
        importance_score: float = 0.5,
    ) -> str:
        """
        Add content to memory.
        
        Args:
            content: Content to add
            importance_score: Importance score (0-1)
        
        Returns:
            Block ID
        """
        token_count = self._estimate_tokens(content)
        
        # Check if we need to compress memory
        if self.current_token_count + token_count > self.max_memory_tokens:
            self._compress_memory()
        
        block_id = f"block_{len(self.memory_blocks)}"
        summary = self._generate_summary(content)
        
        block = MemoryBlock(
            block_id=block_id,
            content=content,
            summary=summary,
            timestamp=datetime.now().isoformat(),
            importance_score=importance_score,
            token_count=token_count,
        )
        
        self.memory_blocks.append(block)
        self.current_token_count += token_count
        
        logger.info(f"Memory added: {block_id} ({token_count} tokens)")
        
        return block_id
    
    def get_memory(self, block_id: str) -> Optional[MemoryBlock]:
        """Get a memory block by ID."""
        for block in self.memory_blocks:
            if block.block_id == block_id:
                return block
        return None
    
    def get_recent_memory(self, num_blocks: int = 5) -> List[MemoryBlock]:
        """Get most recent memory blocks."""
        return self.memory_blocks[-num_blocks:]
    
    def get_important_memory(self, num_blocks: int = 5) -> List[MemoryBlock]:
        """Get most important memory blocks."""
        sorted_blocks = sorted(
            self.memory_blocks,
            key=lambda b: b.importance_score,
            reverse=True,
        )
        return sorted_blocks[:num_blocks]
    
    def get_sliding_window_memory(self) -> List[MemoryBlock]:
        """Get memory using sliding window strategy."""
        return self.memory_blocks[-self.window_size:]
    
    def get_compressed_memory(self) -> str:
        """Get compressed memory as a single string."""
        summaries = []
        
        # Include recent blocks
        recent = self.get_recent_memory(self.window_size)
        for block in recent:
            summaries.append(f"[{block.block_id}] {block.summary}")
        
        # Include important blocks
        important = self.get_important_memory(3)
        for block in important:
            if block not in recent:
                summaries.append(f"[{block.block_id}] {block.summary}")
        
        return "\n".join(summaries)
    
    def _compress_memory(self):
        """Compress memory by removing less important blocks."""
        if not self.memory_blocks:
            return
        
        # Calculate how much we need to remove
        target_tokens = int(self.max_memory_tokens * self.summary_ratio)
        
        # Sort by importance and recency
        scored_blocks = []
        for idx, block in enumerate(self.memory_blocks):
            # Score based on importance and recency
            recency_score = idx / len(self.memory_blocks)
            combined_score = (
                block.importance_score * 0.6 +
                recency_score * 0.4
            )
            scored_blocks.append((combined_score, block))
        
        # Keep high-scoring blocks
        scored_blocks.sort(reverse=True)
        
        kept_blocks = []
        tokens_kept = 0
        
        for score, block in scored_blocks:
            if tokens_kept + block.token_count <= target_tokens:
                kept_blocks.append(block)
                tokens_kept += block.token_count
        
        # Update memory
        self.memory_blocks = kept_blocks
        self.current_token_count = tokens_kept
        
        logger.info(f"Memory compressed: {len(kept_blocks)} blocks, {tokens_kept} tokens")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of content."""
        # Simple summary: first 200 chars + last 100 chars
        if len(content) <= 300:
            return content
        
        first_part = content[:200]
        last_part = content[-100:]
        
        return f"{first_part}...[TRUNCATED]...{last_part}"
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_blocks": len(self.memory_blocks),
            "total_tokens": self.current_token_count,
            "max_tokens": self.max_memory_tokens,
            "usage_percent": (self.current_token_count / self.max_memory_tokens * 100),
            "avg_importance": (
                sum(b.importance_score for b in self.memory_blocks) / len(self.memory_blocks)
                if self.memory_blocks else 0
            ),
        }
    
    def clear_memory(self):
        """Clear all memory."""
        self.memory_blocks = []
        self.current_token_count = 0
        logger.info("Memory cleared")


class ContextCompressor:
    """
    Compresses context for efficient token usage.
    Extracts key information and removes redundancy.
    """
    
    def __init__(self):
        """Initialize context compressor."""
        logger.info("Context Compressor initialized")
    
    def compress_llm_outputs(
        self,
        outputs: List[str],
    ) -> str:
        """
        Compress multiple LLM outputs into a summary.
        
        Args:
            outputs: List of LLM outputs
        
        Returns:
            Compressed summary
        """
        if not outputs:
            return ""
        
        # Extract key points from each output
        key_points = []
        for output in outputs:
            points = self._extract_key_points(output)
            key_points.extend(points)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_points = []
        for point in key_points:
            if point not in seen:
                seen.add(point)
                unique_points.append(point)
        
        return "\n".join(unique_points)
    
    def compress_chat_history(
        self,
        messages: List[Dict[str, str]],
        keep_last_n: int = 5,
    ) -> List[Dict[str, str]]:
        """
        Compress chat history by keeping recent messages and summarizing old ones.
        
        Args:
            messages: List of messages
            keep_last_n: Number of recent messages to keep
        
        Returns:
            Compressed message list
        """
        if len(messages) <= keep_last_n:
            return messages
        
        # Keep recent messages
        recent = messages[-keep_last_n:]
        
        # Summarize older messages
        old_messages = messages[:-keep_last_n]
        summary = self._summarize_messages(old_messages)
        
        # Create summary message
        summary_message = {
            "role": "system",
            "content": f"[PREVIOUS CONVERSATION SUMMARY]\n{summary}",
        }
        
        return [summary_message] + recent
    
    def compress_code_diffs(
        self,
        diffs: List[str],
    ) -> str:
        """
        Compress code diffs by keeping only essential changes.
        
        Args:
            diffs: List of code diffs
        
        Returns:
            Compressed diffs
        """
        essential_diffs = []
        
        for diff in diffs:
            # Keep only lines that start with + or -
            lines = diff.split("\n")
            essential_lines = [
                line for line in lines
                if line.startswith("+") or line.startswith("-")
            ]
            
            if essential_lines:
                essential_diffs.append("\n".join(essential_lines))
        
        return "\n\n".join(essential_diffs)
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text."""
        # Simple extraction: split by sentences and filter
        sentences = text.split(".")
        
        key_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Keep sentences longer than 10 words
            if len(sentence.split()) > 10:
                key_points.append(sentence + ".")
        
        return key_points[:5]  # Keep top 5 points
    
    def _summarize_messages(self, messages: List[Dict[str, str]]) -> str:
        """Summarize a list of messages."""
        summary_parts = []
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Extract first 100 chars of each message
            preview = content[:100] + "..." if len(content) > 100 else content
            summary_parts.append(f"{role}: {preview}")
        
        return "\n".join(summary_parts)


# Global instances
memory_manager = MemoryManager()
context_compressor = ContextCompressor()
