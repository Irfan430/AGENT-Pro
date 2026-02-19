"""
Test Agent Tasks - Tests the agent with sample tasks to verify functionality.
"""

import asyncio
import logging
import json
from typing import Dict, Any

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AgentTester:
    """Tests agent functionality with sample tasks."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize agent tester."""
        self.api_url = api_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(timeout=60)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def test_simple_task(self) -> bool:
        """Test a simple task."""
        logger.info("=" * 60)
        logger.info("TEST 1: Simple Python Code Execution")
        logger.info("=" * 60)
        
        task = {
            "message": "Write a Python script that calculates the sum of numbers 1 to 100 and print the result.",
            "session_id": "test-session-1",
            "auto_execute": True,
        }
        
        try:
            response = await self.session.post(
                f"{self.api_url}/api/chat",
                json=task,
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Task completed successfully")
                logger.info(f"Response: {json.dumps(result, indent=2)[:500]}")
                return True
            else:
                logger.error(f"✗ Task failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            return False
    
    async def test_data_analysis_task(self) -> bool:
        """Test a data analysis task."""
        logger.info("=" * 60)
        logger.info("TEST 2: Data Analysis Task")
        logger.info("=" * 60)
        
        task = {
            "message": "Create a Python script that generates sample data (10 numbers) and calculates mean, median, and standard deviation.",
            "session_id": "test-session-2",
            "auto_execute": True,
        }
        
        try:
            response = await self.session.post(
                f"{self.api_url}/api/chat",
                json=task,
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Data analysis task completed")
                logger.info(f"Response: {json.dumps(result, indent=2)[:500]}")
                return True
            else:
                logger.error(f"✗ Task failed with status {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            return False
    
    async def test_multi_step_task(self) -> bool:
        """Test a multi-step task."""
        logger.info("=" * 60)
        logger.info("TEST 3: Multi-Step Task")
        logger.info("=" * 60)
        
        task = {
            "message": """
            Create a Python script that:
            1. Generates a list of 20 random numbers between 1 and 100
            2. Sorts the list
            3. Finds the maximum and minimum values
            4. Calculates the average
            5. Prints all results in a formatted way
            """,
            "session_id": "test-session-3",
            "auto_execute": True,
        }
        
        try:
            response = await self.session.post(
                f"{self.api_url}/api/chat",
                json=task,
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Multi-step task completed")
                logger.info(f"Response: {json.dumps(result, indent=2)[:500]}")
                return True
            else:
                logger.error(f"✗ Task failed with status {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            return False
    
    async def test_file_operations(self) -> bool:
        """Test file operations task."""
        logger.info("=" * 60)
        logger.info("TEST 4: File Operations")
        logger.info("=" * 60)
        
        task = {
            "message": "Write a Python script that creates a file named 'test.txt' with some sample text, then reads it back and prints the content.",
            "session_id": "test-session-4",
            "auto_execute": True,
        }
        
        try:
            response = await self.session.post(
                f"{self.api_url}/api/chat",
                json=task,
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ File operations task completed")
                logger.info(f"Response: {json.dumps(result, indent=2)[:500]}")
                return True
            else:
                logger.error(f"✗ Task failed with status {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            return False
    
    async def test_continuation_detection(self) -> bool:
        """Test token limit detection and continuation."""
        logger.info("=" * 60)
        logger.info("TEST 5: Continuation Detection")
        logger.info("=" * 60)
        
        # This task is designed to potentially trigger token limits
        task = {
            "message": """
            Write a comprehensive Python script that:
            1. Implements a class for managing a task list
            2. Includes methods for adding, removing, and listing tasks
            3. Implements task prioritization
            4. Includes error handling
            5. Has detailed docstrings for all methods
            6. Includes example usage
            
            Make it as detailed and comprehensive as possible.
            """,
            "session_id": "test-session-5",
            "auto_execute": True,
        }
        
        try:
            response = await self.session.post(
                f"{self.api_url}/api/chat",
                json=task,
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Continuation test completed")
                logger.info(f"Response: {json.dumps(result, indent=2)[:500]}")
                return True
            else:
                logger.error(f"✗ Task failed with status {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests."""
        logger.info("\n" + "=" * 60)
        logger.info("AUTONOMOUS AGENT PRO - TEST SUITE")
        logger.info("=" * 60 + "\n")
        
        results = {
            "simple_task": await self.test_simple_task(),
            "data_analysis": await self.test_data_analysis_task(),
            "multi_step": await self.test_multi_step_task(),
            "file_operations": await self.test_file_operations(),
            "continuation": await self.test_continuation_detection(),
        }
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, passed_flag in results.items():
            status = "✓ PASSED" if passed_flag else "✗ FAILED"
            logger.info(f"{test_name:30} {status}")
        
        logger.info("=" * 60)
        logger.info(f"Total: {passed}/{total} tests passed")
        logger.info("=" * 60 + "\n")
        
        return results


async def main():
    """Run all tests."""
    async with AgentTester() as tester:
        results = await tester.run_all_tests()
        
        # Exit with appropriate code
        exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    asyncio.run(main())
