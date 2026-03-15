"""
Execution service for running compiled programs safely.
Handles runtime execution with timeouts and input/output management.
"""

import subprocess
import os
import platform
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ExecutorService:
    """Service for executing compiled programs safely."""
    
    # Execution timeout (seconds)
    EXECUTION_TIMEOUT = 10
    
    # Maximum output size (bytes) to prevent memory issues
    MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
    
    def execute_c(self, executable_path: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute compiled C program.
        
        Args:
            executable_path: Path to the compiled executable
            input_data: Optional input data for stdin
            
        Returns:
            Dictionary with execution results
        """
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "return_code": None,
            "error": None,
            "timeout": False
        }
        
        try:
            # On Windows, ensure executable has .exe extension if not present
            if self.is_windows and not executable_path.endswith('.exe'):
                # Check if .exe version exists
                exe_path = executable_path + '.exe'
                if os.path.exists(exe_path):
                    executable_path = exe_path
                elif not os.path.exists(executable_path):
                    # Try .exe version
                    executable_path = exe_path
            
            if not os.path.exists(executable_path):
                result["error"] = f"Executable not found: {executable_path}"
                return result
            
            # Prepare input
            input_bytes = input_data.encode("utf-8") if input_data else None
            
            # Execute program with timeout
            # Use absolute path for better compatibility
            abs_executable_path = os.path.abspath(executable_path)
            process = subprocess.Popen(
                [abs_executable_path],
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(abs_executable_path)
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=input_bytes,
                    timeout=self.EXECUTION_TIMEOUT
                )
                
                result["return_code"] = process.returncode
                result["stdout"] = stdout.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE]
                result["stderr"] = stderr.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE]
                
                if process.returncode == 0:
                    result["success"] = True
                else:
                    result["error"] = f"Program exited with code {process.returncode}"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                result["timeout"] = True
                result["error"] = f"Execution timeout exceeded ({self.EXECUTION_TIMEOUT}s)"
                
        except Exception as e:
            logger.error(f"Error executing C program: {e}", exc_info=True)
            result["error"] = f"Execution failed: {str(e)}"
        
        return result
    
    def execute_java(self, class_path: str, class_name: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute compiled Java program.
        
        Args:
            class_path: Path to directory containing .class files
            class_name: Name of the main class
            input_data: Optional input data for stdin
            
        Returns:
            Dictionary with execution results
        """
        result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "return_code": None,
            "error": None,
            "timeout": False
        }
        
        try:
            class_file = os.path.join(class_path, f"{class_name}.class")
            if not os.path.exists(class_file):
                result["error"] = "Class file not found"
                return result
            
            # Prepare input
            input_bytes = input_data.encode("utf-8") if input_data else None
            
            # Execute Java program with timeout
            process = subprocess.Popen(
                ["java", "-cp", class_path, class_name],
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=class_path
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=input_bytes,
                    timeout=self.EXECUTION_TIMEOUT
                )
                
                result["return_code"] = process.returncode
                result["stdout"] = stdout.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE]
                result["stderr"] = stderr.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE]
                
                if process.returncode == 0:
                    result["success"] = True
                else:
                    result["error"] = f"Program exited with code {process.returncode}"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                result["timeout"] = True
                result["error"] = f"Execution timeout exceeded ({self.EXECUTION_TIMEOUT}s)"
                
        except Exception as e:
            logger.error(f"Error executing Java program: {e}", exc_info=True)
            result["error"] = f"Execution failed: {str(e)}"
        
        return result

