"""
Compiler service for C and Java programs.
Handles compilation and error capture.
"""

import subprocess
import tempfile
import os
import shutil
import platform
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CompilerService:
    """Service for compiling C and Java source code."""
    
    # Compilation timeout (seconds)
    COMPILE_TIMEOUT = 30
    
    def __init__(self):
        self.temp_dir = None
        self.is_windows = platform.system() == "Windows"
    
    def _check_compiler_available(self, compiler: str) -> bool:
        """Check if a compiler is available in PATH."""
        # On Windows, try both 'gcc' and 'gcc.exe'
        compiler_names = [compiler]
        if self.is_windows and compiler == "gcc":
            compiler_names = ["gcc", "gcc.exe"]
        
        for comp_name in compiler_names:
            try:
                result = subprocess.run(
                    [comp_name, "--version"],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                # Check if command executed successfully (return code 0)
                if result.returncode == 0:
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return False
    
    def _create_temp_directory(self) -> str:
        """Create a temporary directory for compilation."""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="compiler_debug_")
        return self.temp_dir
    
    def _cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")

    def _refine_error_line(self, code: str, line: Optional[int], message: str) -> Optional[int]:
        """
        Refine the error line number for common compiler off-by-one errors.
        For example, missing semicolons are often reported on the next line.
        """
        if line is None or line <= 1:
            return line
            
        code_lines = code.split('\n')
        if line > len(code_lines):
            return line
            
        msg_lower = message.lower()
        
        # Check for missing semicolon errors
        if "expected ';'" in msg_lower or "missing semicolon" in msg_lower or "';' expected" in msg_lower:
            # GCC often reports missing semicolon on the line AFTER the actual statement,
            # sometimes even multiple lines later if there are blank lines or comments.
            # We look backwards for the first non-empty line that isn't a comment/structural line.
            current_idx = line - 2 # Start at the line preceding the reported line (1-indexed)
            
            # Search back up to 3 lines to find the actual statement missing a semicolon
            search_depth = 0
            while current_idx >= 0 and search_depth < 3:
                prev_line = code_lines[current_idx].strip()
                
                # Skip empty lines or comment-only lines
                if not prev_line or prev_line.startswith('//') or prev_line.startswith('/*') or prev_line.startswith('*'):
                    current_idx -= 1
                    search_depth += 1
                    continue
                
                # If we found a line that doesn't end in structural characters
                if not any(prev_line.endswith(c) for c in [';', '{', '}', ':']):
                    # And isn't a control structure start
                    if not any(prev_line.startswith(kw) for kw in ['if', 'for', 'while', 'switch', 'else']):
                        logger.info(f"Refining error line from {line} to {current_idx + 1} due to missing semicolon")
                        return current_idx + 1
                
                # If we find a line with a semicolon or brace, it means we went too far back. Stop searching.
                if any(prev_line.endswith(c) for c in [';', '{', '}', ':']):
                    break
                    
                current_idx -= 1
                search_depth += 1
                        
        return line
    
    def compile_c(self, code: str) -> Dict[str, Any]:
        """
        Compile C source code using gcc.
        
        Args:
            code: C source code
            
        Returns:
            Dictionary with compilation status and errors
        """
        result = {
            "success": False,
            "executable_path": None,
            "errors": [],
            "warnings": [],
            "stderr": ""
        }
        
        try:
            # Check if gcc is available
            if not self._check_compiler_available("gcc"):
                if self.is_windows:
                    error_msg = (
                        "GCC compiler not found. To install GCC on Windows:\n"
                        "1. Download MinGW-w64 from: https://www.mingw-w64.org/downloads/\n"
                        "   OR install via MSYS2: https://www.msys2.org/\n"
                        "   OR use Chocolatey: choco install mingw\n"
                        "2. Add MinGW bin directory to your PATH environment variable\n"
                        "   (e.g., C:\\mingw64\\bin)\n"
                        "3. Restart your terminal/IDE after installation\n"
                        "4. Verify installation by running: gcc --version"
                    )
                else:
                    error_msg = (
                        "GCC compiler not found. To install GCC:\n"
                        "- Ubuntu/Debian: sudo apt-get install gcc\n"
                        "- Fedora/RHEL: sudo dnf install gcc\n"
                        "- macOS: xcode-select --install (or use Homebrew: brew install gcc)\n"
                        "Ensure GCC is in your PATH and restart your terminal."
                    )
                result["errors"].append({
                    "line": 1,
                    "message": error_msg,
                    "raw": "gcc compiler not found"
                })
                return result
            
            temp_dir = self._create_temp_directory()
            source_file = os.path.join(temp_dir, "program.c")
            # Add .exe extension on Windows
            executable_name = "program.exe" if self.is_windows else "program"
            executable = os.path.join(temp_dir, executable_name)
            
            # Write source code to file
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Compile using gcc
            compile_cmd = [
                "gcc",
                "-o", executable,
                source_file,
                "-Wall",  # Enable all warnings
                "-std=c11"  # Use C11 standard
            ]
            
            process = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8', # Force UTF-8 encoding
                errors='replace', # Replace invalid characters
                timeout=self.COMPILE_TIMEOUT,
                cwd=temp_dir
            )
            
            if process.returncode == 0:
                # Verify executable exists (with correct extension)
                if os.path.exists(executable):
                    result["success"] = True
                    result["executable_path"] = executable
                else:
                    result["errors"].append({
                        "line": None,
                        "message": "Compilation succeeded but executable not found",
                        "raw": "Executable file not created"
                    })
            else:
                result["stderr"] = process.stderr if process.stderr else ""
                # Parse errors and warnings with line numbers
                import re
                stderr_content = process.stderr if process.stderr else ""
                error_lines = stderr_content.split("\n")
                for line in error_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip "In function" context lines as they are not errors
                    if "in function" in line.lower() and not "error:" in line.lower():
                        continue
                        
                    if "error:" in line.lower():
                        # Try to extract line number from gcc error format: file.c:line:column: error: message
                        # Also handle formats like: file.c:line: error: or file.c:line:column: error:
                        # Regex to capture line number. Matches :123: or :123:45: before "error:"
                        line_match = re.search(r':(\d+)(?::\d+)?:\s*(?:fatal\s+)?error:', line, re.IGNORECASE)
                        if line_match:
                            line_num = int(line_match.group(1))
                            line_num = self._refine_error_line(code, line_num, line)
                            error_info = {
                                "line": line_num,
                                "message": line,
                                "raw": line
                            }
                            result["errors"].append(error_info)
                        else:
                            # Try alternative format: error at line X
                            alt_match = re.search(r'(?:error|Error).*?line\s+(\d+)', line, re.IGNORECASE)
                            if alt_match:
                                line_num = int(alt_match.group(1))
                                line_num = self._refine_error_line(code, line_num, line)
                                error_info = {
                                    "line": line_num,
                                    "message": line,
                                    "raw": line
                                }
                                result["errors"].append(error_info)
                            else:
                                result["errors"].append({"line": None, "message": line, "raw": line})
                    elif "warning:" in line.lower():
                        result["warnings"].append(line)
                    elif line and not any(x in line.lower() for x in ["note:", "warning:"]):
                        # Only add if it's not a continuation line
                        if result["errors"] and isinstance(result["errors"][-1], dict):
                            result["errors"][-1]["message"] += "\n" + line
                        # If we haven't started an error yet, ignore this line (it's likely context like "In function...")
                        # unless it explicitly looks like an error start
            
        except subprocess.TimeoutExpired:
            result["errors"].append({
                "line": None,
                "message": "Compilation timeout exceeded",
                "raw": "Compilation timeout exceeded"
            })
        except FileNotFoundError:
            if self.is_windows:
                error_msg = (
                    "GCC compiler not found. To install GCC on Windows:\n"
                    "1. Download MinGW-w64 from: https://www.mingw-w64.org/downloads/\n"
                    "   OR install via MSYS2: https://www.msys2.org/\n"
                    "   OR use Chocolatey: choco install mingw\n"
                    "2. Add MinGW bin directory to your PATH environment variable\n"
                    "   (e.g., C:\\mingw64\\bin)\n"
                    "3. Restart your terminal/IDE after installation\n"
                    "4. Verify installation by running: gcc --version"
                )
            else:
                error_msg = (
                    "GCC compiler not found. To install GCC:\n"
                    "- Ubuntu/Debian: sudo apt-get install gcc\n"
                    "- Fedora/RHEL: sudo dnf install gcc\n"
                    "- macOS: xcode-select --install (or use Homebrew: brew install gcc)\n"
                    "Ensure GCC is in your PATH and restart your terminal."
                )
            result["errors"].append({
                "line": 1,
                "message": error_msg,
                "raw": "gcc not found"
            })
        except Exception as e:
            logger.error(f"Error compiling C code: {e}", exc_info=True)
            error_msg = str(e)
            # Extract line number from error if possible
            line_num = None
            if "line" in error_msg.lower():
                import re
                line_match = re.search(r'line\s+(\d+)', error_msg, re.IGNORECASE)
                if line_match:
                    line_num = int(line_match.group(1))
            
            result["errors"].append({
                "line": line_num or 1,
                "message": f"Compilation failed: {error_msg}",
                "raw": error_msg
            })
        
        return result
    
    def compile_java(self, code: str) -> Dict[str, Any]:
        """
        Compile Java source code using javac.
        
        Args:
            code: Java source code
            
        Returns:
            Dictionary with compilation status and errors
        """
        result = {
            "success": False,
            "class_path": None,
            "class_name": None,
            "errors": [],
            "warnings": [],
            "stderr": ""
        }
        
        try:
            # Check if javac is available
            if not self._check_compiler_available("javac"):
                result["errors"].append({
                    "line": 1,
                    "message": "javac compiler not found. Please install Java JDK and ensure it's in your PATH.",
                    "raw": "javac compiler not found"
                })
                return result
            
            temp_dir = self._create_temp_directory()
            
            # Extract class name from code (simple heuristic)
            class_name = self._extract_java_class_name(code)
            if not class_name:
                result["errors"].append({
                    "line": 1,
                    "message": "Could not determine Java class name. Ensure code contains a public class.",
                    "raw": "Class name not found"
                })
                return result
            
            source_file = os.path.join(temp_dir, f"{class_name}.java")
            
            # Write source code to file
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Compile using javac
            compile_cmd = [
                "javac",
                "-encoding", "UTF-8",
                "-Xlint:all",  # Enable all warnings
                source_file
            ]
            
            process = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8', # Force UTF-8 encoding
                errors='replace', # Replace invalid characters
                timeout=self.COMPILE_TIMEOUT,
                cwd=temp_dir
            )
            
            if process.returncode == 0:
                # Verify class file exists
                class_file = os.path.join(temp_dir, f"{class_name}.class")
                if os.path.exists(class_file):
                    result["success"] = True
                    result["class_path"] = temp_dir
                    result["class_name"] = class_name
                else:
                    result["errors"].append({
                        "line": None,
                        "message": "Compilation succeeded but class file not found",
                        "raw": "Class file not created"
                    })
            else:
                result["stderr"] = process.stderr if process.stderr else ""
                # Parse errors and warnings with line numbers
                import re
                stderr_content = process.stderr if process.stderr else ""
                error_lines = stderr_content.split("\n")
                for line in error_lines:
                    line = line.strip()
                    if not line:
                        continue
                    if "error:" in line.lower():
                        # Try to extract line number from javac error format: Main.java:line: error: message
                        line_match = re.search(r'\.java:(\d+):\s*error:', line)
                        if line_match:
                            line_num = int(line_match.group(1))
                            line_num = self._refine_error_line(code, line_num, line)
                            error_info = {
                                "line": line_num,
                                "message": line,
                                "raw": line
                            }
                            result["errors"].append(error_info)
                        else:
                            result["errors"].append({"line": None, "message": line, "raw": line})
                    elif "warning:" in line.lower():
                        result["warnings"].append(line)
                    elif line and not any(x in line.lower() for x in ["note:", "warning:"]):
                        # Only add if it's not a continuation line
                        if result["errors"] and isinstance(result["errors"][-1], dict):
                            result["errors"][-1]["message"] += "\n" + line
                        else:
                            result["errors"].append({"line": None, "message": line, "raw": line})
            
        except subprocess.TimeoutExpired:
            result["errors"].append({
                "line": None,
                "message": "Compilation timeout exceeded",
                "raw": "Compilation timeout exceeded"
            })
        except FileNotFoundError:
            result["errors"].append({
                "line": 1,
                "message": "javac compiler not found. Please install Java JDK and ensure it's in your PATH.",
                "raw": "javac not found"
            })
        except Exception as e:
            logger.error(f"Error compiling Java code: {e}", exc_info=True)
            error_msg = str(e)
            # Extract line number from error if possible
            line_num = None
            if "line" in error_msg.lower():
                import re
                line_match = re.search(r'line\s+(\d+)', error_msg, re.IGNORECASE)
                if line_match:
                    line_num = int(line_match.group(1))
            
            result["errors"].append({
                "line": line_num or 1,
                "message": f"Compilation failed: {error_msg}",
                "raw": error_msg
            })
        
        return result
    
    def _extract_java_class_name(self, code: str) -> Optional[str]:
        """Extract the public class name from Java source code."""
        import re
        # Look for public class declaration
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            return match.group(1)
        # Fallback: look for any class declaration
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)
        return None
    
    def __del__(self):
        """Cleanup on destruction."""
        self._cleanup()

