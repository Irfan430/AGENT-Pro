"""
Test DeepSeek API integration and verify API key validity.
"""

import os
import asyncio
import logging
from typing import Optional

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_deepseek_api_connection() -> bool:
    """
    Test DeepSeek API connection with a simple request.
    
    Returns:
        True if API key is valid, False otherwise
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        logger.error("DEEPSEEK_API_KEY environment variable not set")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Say 'API connection successful' in one sentence.",
                        }
                    ],
                    "max_tokens": 50,
                    "temperature": 0.5,
                },
            )
        
        if response.status_code == 200:
            logger.info("✓ DeepSeek API connection successful")
            logger.info(f"Response: {response.json()}")
            return True
        elif response.status_code == 401:
            logger.error("✗ Invalid API key (401 Unauthorized)")
            return False
        else:
            logger.error(f"✗ API error: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"✗ Connection error: {str(e)}")
        return False


def test_deepseek_sync() -> bool:
    """Synchronous wrapper for testing."""
    return asyncio.run(test_deepseek_api_connection())


if __name__ == "__main__":
    success = test_deepseek_sync()
    exit(0 if success else 1)
