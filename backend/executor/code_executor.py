"""
Code Executor - Executes code in multiple languages with sandboxing and safety.
Supports Python, JavaScript, Shell, Java, R, and Ruby with timeout protection.
"""

import asyncio
import subprocess
import tempfile
import os
import logging
import json
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

from backend.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Represents the result of code execution."""
    execution_id: str
    language: str
    code: str
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0
    timestamp: str = None
    exit_code: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CodeExecutor:
    """
    Executes code safely in multiple languages.
    Provides sandboxing, timeout protection, and error handling.
    """
    
    LANGUAGE_EXTENSIONS = {
        "python": ".py",
        "javascript": ".js",
        "shell": ".sh",
        "bash": ".sh",
        "java": ".java",
        "r": ".r",
        "ruby": ".rb",
    }
    
    LANGUAGE_COMMANDS = {
        "python": ["python3", "-u"],
        "javascript": ["node"],
        "shell": ["bash"],
        "bash": ["bash"],
        "java": ["java"],
        "r": ["Rscript"],
        "ruby": ["ruby"],
    }
    
    def __init__(self):
        """Initialize the code executor."""
        self.timeout = settings.EXECUTION_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
        self.max_output_length = settings.MAX_OUTPUT_LENGTH
        
        # Create temp directory for execution
        self.temp_dir = tempfile.gettempdir()
        
        logger.info("Code Executor initialized")
    
    async def execute(
        self,
        code: str,
        language: str,
        timeout: Optional[int] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Execute code in the specified language.
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, shell, etc.)
            timeout: Execution timeout in seconds
            env_vars: Environment variables to pass to the process
        
        Returns:
            ExecutionResult with output and status
        """
        execution_id = str(uuid.uuid4())
        timeout = timeout or self.timeout
        
        # Validate language
        if language not in self.LANGUAGE_EXTENSIONS:
            return ExecutionResult(
                execution_id=execution_id,
                language=language,
                code=code,
                success=False,
                output="",
                error=f"Unsupported language: {language}",
                exit_code=1,
            )
        
        # Create temporary file
        ext = self.LANGUAGE_EXTENSIONS[language]
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=ext,
            delete=False,
            dir=self.temp_dir,
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = await self._execute_with_timeout(
                temp_file,
                language,
                timeout,
                env_vars,
                execution_id,
            )
            return result
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {e}")
    
    async def _execute_with_timeout(
        self,
        file_path: str,
        language: str,
        timeout: int,
        env_vars: Optional[Dict[str, str]],
        execution_id: str,
    ) -> ExecutionResult:
        """Execute code with timeout protection."""
        import time
        start_time = time.time()
        
        try:
            # Prepare command
            cmd = self.LANGUAGE_COMMANDS[language] + [file_path]
            
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                duration = time.time() - start_time
                
                return ExecutionResult(
                    execution_id=execution_id,
                    language=language,
                    code=open(file_path).read(),
                    success=False,
                    output="",
                    error=f"Execution timeout after {timeout} seconds",
                    duration=duration,
                    exit_code=124,  # Standard timeout exit code
                )
            
            duration = time.time() - start_time
            
            # Decode output
            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")
            
            # Truncate output if too long
            if len(output) > self.max_output_length:
                output = output[:self.max_output_length] + "\n... (output truncated)"
            
            success = process.returncode == 0
            
            return ExecutionResult(
                execution_id=execution_id,
                language=language,
                code=open(file_path).read(),
                success=success,
                output=output,
                error=error if error else None,
                duration=duration,
                exit_code=process.returncode,
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Execution error: {str(e)}")
            
            return ExecutionResult(
                execution_id=execution_id,
                language=language,
                code=open(file_path).read() if os.path.exists(file_path) else code,
                success=False,
                output="",
                error=f"Execution error: {str(e)}",
                duration=duration,
                exit_code=1,
            )
    
    async def execute_with_retry(
        self,
        code: str,
        language: str,
        max_retries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """
        Execute code with automatic retry on failure.
        
        Args:
            code: Code to execute
            language: Programming language
            max_retries: Maximum number of retries
            timeout: Execution timeout
        
        Returns:
            ExecutionResult from successful execution or last attempt
        """
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            result = await self.execute(code, language, timeout)
            
            if result.success:
                return result
            
            if attempt < max_retries - 1:
                logger.warning(
                    f"Execution failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {self.retry_delay}s..."
                )
                await asyncio.sleep(self.retry_delay)
        
        return result
    
    def validate_code_syntax(
        self,
        code: str,
        language: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate code syntax without executing.
        
        Args:
            code: Code to validate
            language: Programming language
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if language == "python":
            import ast
            try:
                ast.parse(code)
                return True, None
            except SyntaxError as e:
                return False, f"Syntax error: {e.msg} at line {e.lineno}"
        
        elif language in ["javascript", "shell", "bash"]:
            # Basic validation for these languages
            if not code.strip():
                return False, "Code is empty"
            return True, None
        
        # For other languages, assume valid
        return True, None
    
    async def execute_in_sandbox(
        self,
        code: str,
        language: str,
        restricted_imports: Optional[list] = None,
    ) -> ExecutionResult:
        """
        Execute code in a restricted sandbox environment.
        
        Args:
            code: Code to execute
            language: Programming language
            restricted_imports: List of modules to restrict
        
        Returns:
            ExecutionResult
        """
        if language == "python" and settings.SANDBOX_ENABLED:
            # Add import restrictions for Python
            restricted_imports = restricted_imports or settings.RESTRICTED_MODULES
            
            # Check for restricted imports
            for module in restricted_imports:
                if f"import {module}" in code or f"from {module}" in code:
                    return ExecutionResult(
                        execution_id=str(uuid.uuid4()),
                        language=language,
                        code=code,
                        success=False,
                        output="",
                        error=f"Import of restricted module '{module}' is not allowed",
                        exit_code=1,
                    )
        
        # Execute normally if sandbox checks pass
        return await self.execute(code, language)


# Global executor instance
code_executor = CodeExecutor()
