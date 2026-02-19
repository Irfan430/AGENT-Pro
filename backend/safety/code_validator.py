"""
Code Validator - Validates code for security and safety before execution.
Implements sandboxing rules and restricts dangerous operations.
"""

import ast
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from backend.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation."""
    is_safe: bool
    issues: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    suggestions: List[str]
    can_execute: bool


class CodeValidator:
    """
    Validates code for security and safety issues.
    Detects dangerous operations and provides suggestions.
    """
    
    # Dangerous Python modules that should be restricted
    DANGEROUS_MODULES = {
        "os": "System operations",
        "sys": "System access",
        "subprocess": "Process execution",
        "socket": "Network operations",
        "requests": "HTTP requests",
        "urllib": "URL operations",
        "pickle": "Deserialization",
        "eval": "Code evaluation",
        "exec": "Code execution",
        "compile": "Code compilation",
        "__import__": "Dynamic imports",
    }
    
    # Dangerous Python functions
    DANGEROUS_FUNCTIONS = {
        "eval": "Code evaluation",
        "exec": "Code execution",
        "compile": "Code compilation",
        "open": "File operations",
        "input": "User input",
        "__import__": "Dynamic imports",
        "getattr": "Attribute access",
        "setattr": "Attribute modification",
        "delattr": "Attribute deletion",
    }
    
    # Dangerous shell commands
    DANGEROUS_SHELL_COMMANDS = {
        "rm": "File deletion",
        "rmdir": "Directory deletion",
        "mkfs": "Filesystem formatting",
        "dd": "Disk operations",
        "kill": "Process termination",
        "killall": "Process termination",
        "shutdown": "System shutdown",
        "reboot": "System reboot",
        "halt": "System halt",
        "passwd": "Password change",
        "sudo": "Privilege escalation",
        "chmod": "Permission modification",
        "chown": "Ownership modification",
    }
    
    def __init__(self):
        """Initialize the code validator."""
        self.restricted_modules = settings.RESTRICTED_MODULES
        logger.info("Code Validator initialized")
    
    def validate_python(self, code: str) -> ValidationResult:
        """
        Validate Python code for security issues.
        
        Args:
            code: Python code to validate
        
        Returns:
            ValidationResult with issues and suggestions
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for syntax errors
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "severity": "high",
                "issue": f"Syntax error: {e.msg}",
                "line": e.lineno or 0,
            })
            return ValidationResult(
                is_safe=False,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions,
                can_execute=False,
            )
        
        # Analyze AST for dangerous operations
        for node in ast.walk(tree):
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name in self.DANGEROUS_MODULES:
                        if module_name in self.restricted_modules:
                            issues.append({
                                "severity": "high",
                                "issue": f"Restricted module import: {module_name}",
                                "line": node.lineno,
                            })
                        else:
                            warnings.append({
                                "severity": "medium",
                                "issue": f"Dangerous module: {module_name} ({self.DANGEROUS_MODULES[module_name]})",
                                "line": node.lineno,
                            })
            
            # Check for dangerous from imports
            elif isinstance(node, ast.ImportFrom):
                module_name = (node.module or "").split(".")[0]
                if module_name in self.DANGEROUS_MODULES:
                    if module_name in self.restricted_modules:
                        issues.append({
                            "severity": "high",
                            "issue": f"Restricted module import: {module_name}",
                            "line": node.lineno,
                        })
                    else:
                        warnings.append({
                            "severity": "medium",
                            "issue": f"Dangerous module: {module_name}",
                            "line": node.lineno,
                        })
            
            # Check for dangerous function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.DANGEROUS_FUNCTIONS:
                        if func_name in ["eval", "exec", "compile"]:
                            issues.append({
                                "severity": "high",
                                "issue": f"Dangerous function: {func_name}",
                                "line": node.lineno,
                            })
                        else:
                            warnings.append({
                                "severity": "medium",
                                "issue": f"Potentially dangerous function: {func_name}",
                                "line": node.lineno,
                            })
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r"__.*__", "Magic method access"),
            (r"globals\(\)", "Global namespace access"),
            (r"locals\(\)", "Local namespace access"),
            (r"vars\(\)", "Variable access"),
            (r"dir\(\)", "Directory listing"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, code):
                warnings.append({
                    "severity": "medium",
                    "issue": f"Potentially dangerous pattern: {description}",
                    "line": 0,
                })
        
        # Generate suggestions
        if issues:
            suggestions.append("Remove or replace dangerous operations")
        
        if warnings:
            suggestions.append("Review and validate dangerous operations")
        
        if not issues and not warnings:
            suggestions.append("Code appears safe to execute")
        
        is_safe = len(issues) == 0
        can_execute = is_safe or len(issues) == 0  # Can execute if no critical issues
        
        return ValidationResult(
            is_safe=is_safe,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
            can_execute=can_execute,
        )
    
    def validate_shell(self, code: str) -> ValidationResult:
        """
        Validate shell code for dangerous commands.
        
        Args:
            code: Shell code to validate
        
        Returns:
            ValidationResult with issues and suggestions
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Split into commands
        commands = code.split(";")
        
        for i, cmd in enumerate(commands):
            cmd = cmd.strip()
            if not cmd:
                continue
            
            # Extract command name
            parts = cmd.split()
            if not parts:
                continue
            
            command_name = parts[0].split("/")[-1]  # Get last part after /
            
            # Check for dangerous commands
            if command_name in self.DANGEROUS_SHELL_COMMANDS:
                issues.append({
                    "severity": "high",
                    "issue": f"Dangerous command: {command_name} ({self.DANGEROUS_SHELL_COMMANDS[command_name]})",
                    "line": i + 1,
                })
            
            # Check for pipe to dangerous commands
            if "|" in cmd:
                pipe_parts = cmd.split("|")
                for pipe_cmd in pipe_parts[1:]:
                    pipe_cmd = pipe_cmd.strip().split()[0]
                    if pipe_cmd in self.DANGEROUS_SHELL_COMMANDS:
                        warnings.append({
                            "severity": "high",
                            "issue": f"Piping to dangerous command: {pipe_cmd}",
                            "line": i + 1,
                        })
        
        # Generate suggestions
        if issues:
            suggestions.append("Review dangerous commands before execution")
        
        if not issues and not warnings:
            suggestions.append("Shell code appears safe")
        
        is_safe = len(issues) == 0
        can_execute = is_safe
        
        return ValidationResult(
            is_safe=is_safe,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
            can_execute=can_execute,
        )
    
    def validate_javascript(self, code: str) -> ValidationResult:
        """
        Validate JavaScript code for security issues.
        
        Args:
            code: JavaScript code to validate
        
        Returns:
            ValidationResult with issues and suggestions
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r"eval\s*\(", "eval() function"),
            (r"Function\s*\(", "Function constructor"),
            (r"setTimeout\s*\(\s*['\"].*['\"]", "setTimeout with string"),
            (r"setInterval\s*\(\s*['\"].*['\"]", "setInterval with string"),
            (r"document\.write", "document.write"),
            (r"innerHTML\s*=", "innerHTML assignment"),
            (r"dangerouslySetInnerHTML", "dangerouslySetInnerHTML"),
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, code):
                warnings.append({
                    "severity": "medium",
                    "issue": f"Potentially dangerous: {description}",
                    "line": 0,
                })
        
        # Generate suggestions
        if warnings:
            suggestions.append("Review and validate dangerous patterns")
        else:
            suggestions.append("JavaScript code appears safe")
        
        is_safe = len(issues) == 0
        can_execute = True  # JavaScript in Node.js is relatively safe
        
        return ValidationResult(
            is_safe=is_safe,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
            can_execute=can_execute,
        )
    
    def validate(self, code: str, language: str) -> ValidationResult:
        """
        Validate code based on language.
        
        Args:
            code: Code to validate
            language: Programming language
        
        Returns:
            ValidationResult
        """
        if language == "python":
            return self.validate_python(code)
        elif language in ["shell", "bash"]:
            return self.validate_shell(code)
        elif language == "javascript":
            return self.validate_javascript(code)
        else:
            # For other languages, return safe by default
            return ValidationResult(
                is_safe=True,
                issues=[],
                warnings=[],
                suggestions=["Language validation not implemented"],
                can_execute=True,
            )


# Global validator instance
code_validator = CodeValidator()
