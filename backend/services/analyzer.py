"""
Main analyzer service that orchestrates compilation, execution, and LLM analysis.
"""

import logging
import re
from typing import Dict, Any, Optional
from services.compiler import CompilerService
from services.executor import ExecutorService
from services.llm_service import LLMService
from services.java_fixer import JavaCodeFixer

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Main service for analyzing code with AI-powered explanations."""
    
    def __init__(self):
        self.compiler = CompilerService()
        self.executor = ExecutorService()
        self.java_fixer = JavaCodeFixer()
        try:
            self.llm = LLMService()
        except Exception as e:
            logger.warning(f"Failed to initialize LLM service: {e}. AI explanations will be limited.")
            self.llm = None
    
    async def analyze(
        self,
        language: str,
        code: str,
        input_data: Optional[str] = None,
        expected_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform complete code analysis including compilation, execution, and LLM explanation.
        
        Args:
            language: Programming language ('C' or 'JAVA')
            code: Source code to analyze
            input_data: Optional input for program execution
            expected_output: Optional expected output for comparison
            
        Returns:
            Complete analysis result dictionary
        """
        result = {
            "compile_errors": {},
            "runtime_errors": {},
            "output_analysis": {},
            "llm_explanation": {},
            "execution_success": False,
            "program_output": None
        }
        
        try:
            # Step 1: Compile code
            compile_result = self._compile(language, code)
            result["compile_errors"] = compile_result
            
            # Step 2: Execute if compilation successful
            if compile_result.get("success"):
                runtime_result = self._execute(
                    language, compile_result, input_data
                )
                result["runtime_errors"] = runtime_result
                
                # If execution was successful, include output
                if runtime_result.get("success"):
                    result["execution_success"] = True
                    result["program_output"] = runtime_result.get("stdout", "")
                    
                    # Step 3: Compare output if expected output provided (only when execution succeeds)
                    if expected_output and expected_output.strip():
                        actual_stdout = runtime_result.get("stdout", "")
                        output_analysis = self._analyze_output(
                            actual_stdout,
                            expected_output
                        )
                        result["output_analysis"] = output_analysis
                        # Log for debugging
                        logger.info(f"Output comparison: Expected='{expected_output.strip()}', Actual='{actual_stdout.strip()}', Match={output_analysis.get('match')}")
                    else:
                        result["output_analysis"] = {
                            "match": None,
                            "message": "No expected output provided for comparison",
                            "actual": runtime_result.get("stdout", "")
                        }
                else:
                    # Execution failed - don't compare output
                    result["output_analysis"] = {
                        "match": None,
                        "message": "Cannot compare output: execution failed",
                        "actual": None
                    }
            else:
                # Compilation failed - no runtime errors possible (code never ran)
                result["runtime_errors"] = {
                    "success": True,  # No runtime errors (code didn't run)
                    "error": None,
                    "stderr": "",
                    "stdout": ""
                }
                runtime_result = None
                # Set output_analysis for compilation failure case
                result["output_analysis"] = {
                    "match": None,
                    "message": "Cannot compare output: compilation failed",
                    "actual": None
                }
            
            # Step 4: Generate LLM explanation (if we have errors, output mismatch, or need explanation)
            has_errors = (
                not compile_result.get("success") or
                (runtime_result is not None and not runtime_result.get("success")) or
                (result.get("output_analysis", {}).get("match") is False)
            )
            
            if self.llm and has_errors:
                # Check if LLM service is actually available before using it
                if hasattr(self.llm, 'is_available') and not self.llm.is_available():
                    logger.warning("LLM service initialized but not available (client/model is None)")
                    result["llm_explanation"] = {
                        "summary": "Analysis completed. Review errors below.",
                        "cause": "LLM service not available. Please check your GEMINI_API_KEY configuration in backend/.env file and restart the backend server.",
                        "fix": "To fix: 1) Verify GEMINI_API_KEY in backend/.env file, 2) Run 'python check_api_key.py' to diagnose, 3) Restart the backend server.",
                        "corrected_code": None
                    }
                else:
                    try:
                        # Store compile_errors in a local variable for use in validation
                        compile_errors = result["compile_errors"]
                        
                        # Get runtime_errors (will be empty dict with success:True if compilation failed)
                        runtime_errors_for_llm = result.get("runtime_errors", {
                            "success": True,
                            "error": None,
                            "stderr": "",
                            "stdout": ""
                        })
                        
                        llm_explanation = self.llm.generate_explanation(
                            language=language,
                            code=code,
                            compile_errors=compile_errors,
                            runtime_errors=runtime_errors_for_llm,
                            output_analysis=result.get("output_analysis", {})
                        )
                        
                        # Merge additional errors found by LLM into compile_errors
                        if llm_explanation.get("additional_errors"):
                            additional_errors = llm_explanation["additional_errors"]
                            if isinstance(additional_errors, list):
                                current_errors = compile_errors.get("errors", [])
                                existing_lines = set()
                                
                                # Track existing error lines to avoid duplicates
                                for err in current_errors:
                                    if isinstance(err, dict) and err.get("line"):
                                        existing_lines.add(int(err["line"]))
                                
                                # Add new errors
                                for err in additional_errors:
                                    if isinstance(err, dict) and err.get("line"):
                                        try:
                                            line = int(err["line"])
                                            if line not in existing_lines:
                                                msg = err.get("message", "Error detected by AI")
                                                current_errors.append({
                                                    "line": line,
                                                    "message": f"(AI Detected) {msg}",
                                                    "raw": msg
                                                })
                                                existing_lines.add(line)
                                        except (ValueError, TypeError):
                                            continue
                                
                                # Update success status if we added errors
                                if len(current_errors) > 0:
                                    compile_errors["success"] = False
                                    compile_errors["errors"] = current_errors
                                    # Update the result object as well
                                    result["compile_errors"] = compile_errors
                        
                        # Validate that corrected_code is actually different from original code
                        if llm_explanation.get("corrected_code"):
                            corrected = llm_explanation["corrected_code"].strip()
                            original = code.strip()
                            
                            # Normalize both for comparison (handle different line endings, whitespace, blank lines)
                            import re
                            
                            # Remove all blank lines and normalize whitespace
                            def normalize_code(text):
                                # Remove blank lines (lines with only whitespace)
                                lines = [line.rstrip() for line in text.split('\n')]
                                non_empty_lines = [line for line in lines if line.strip()]
                                # Join and normalize whitespace
                                normalized = ' '.join(' '.join(line.split()) for line in non_empty_lines)
                                return normalized.lower()
                            
                            corrected_normalized = normalize_code(corrected)
                            original_normalized = normalize_code(original)
                            
                            # Also check if the code actually fixes the errors by checking for common error patterns
                            has_fixes = False
                            if compile_errors.get("errors"):
                                # Check if common fixes are present
                                error_text = str(compile_errors["errors"]).lower()
                                corrected_lower = corrected.lower()
                                
                                # Check for common Java fixes
                                if "missing []" in error_text or "array" in error_text:
                                    if "string[]" in corrected_lower and "string args" in original.lower():
                                        has_fixes = True
                                if "missing semicolon" in error_text or "';' expected" in error_text:
                                    # Count semicolons - corrected should have more
                                    if corrected.count(';') > original.count(';'):
                                        has_fixes = True
                                if "incompatible types" in error_text or "cannot convert" in error_text:
                                    # Check if string literals were removed from int assignments
                                    if '"20"' in original and '"20"' not in corrected:
                                        has_fixes = True
                                if "missing closing parenthesis" in error_text or "')' expected" in error_text:
                                    if corrected.count('(') == corrected.count(')') and original.count('(') != original.count(')'):
                                        has_fixes = True
                                if "missing {" in error_text or "'{' expected" in error_text:
                                    if corrected.count('{') > original.count('{'):
                                        has_fixes = True
                                if "cannot find symbol" in error_text or "not defined" in error_text:
                                    # Check if undefined symbols were removed or defined
                                    if "zero" in original.lower() and "zero" not in corrected_lower:
                                        has_fixes = True
                                    if "undeclaredmethod" in original.lower() and "undeclaredmethod" not in corrected_lower:
                                        has_fixes = True
                            
                            # If corrected code is same as original (after normalization), it's not actually fixed
                            if corrected_normalized == original_normalized:
                                logger.warning(f"LLM returned corrected_code identical to original code (after normalization). Original length: {len(original)}, Corrected length: {len(corrected)}")
                                logger.debug(f"Original code preview: {original[:200]}...")
                                logger.debug(f"Corrected code preview: {corrected[:200]}...")
                                
                                # Try programmatic fix as fallback
                                if language.lower() == "java" and compile_errors.get("errors"):
                                    logger.info("Attempting programmatic fix for Java code...")
                                    programmatic_fix = self.java_fixer.apply_fixes(code, compile_errors)
                                    if programmatic_fix != code:
                                        programmatic_normalized = normalize_code(programmatic_fix)
                                        if programmatic_normalized != original_normalized:
                                            logger.info("Programmatic fix applied successfully as fallback")
                                            llm_explanation["corrected_code"] = programmatic_fix
                                        else:
                                            logger.warning("Programmatic fix also returned unchanged code")
                                            llm_explanation["corrected_code"] = None
                                    else:
                                        logger.warning("Programmatic fixer couldn't fix the code")
                                        llm_explanation["corrected_code"] = None
                                else:
                                    # Don't set corrected_code if it's the same - let frontend handle fallback
                                    llm_explanation["corrected_code"] = None
                            elif not has_fixes and compile_errors.get("errors"):
                                # Even if normalized text differs, check if actual fixes were applied
                                logger.warning(f"Corrected code differs in formatting but may not fix errors. Checking if fixes were applied...")
                                
                                # Try programmatic fix as fallback if LLM didn't fix properly
                                if language.lower() == "java":
                                    logger.info("LLM fix may be incomplete, attempting programmatic fix as supplement...")
                                    programmatic_fix = self.java_fixer.apply_fixes(code, compile_errors)
                                    programmatic_normalized = normalize_code(programmatic_fix)
                                    # If programmatic fix is better (more different from original), use it
                                    if programmatic_normalized != original_normalized and programmatic_normalized != corrected_normalized:
                                        # Check which one has more fixes
                                        orig_semicolons = original.count(';')
                                        llm_semicolons = corrected.count(';')
                                        prog_semicolons = programmatic_fix.count(';')
                                        
                                        # Use programmatic fix if it has more semicolons (more fixes applied)
                                        if prog_semicolons > llm_semicolons:
                                            logger.info("Using programmatic fix as it applies more corrections")
                                            llm_explanation["corrected_code"] = programmatic_fix
                                        else:
                                            logger.info(f"Corrected code differs from original. Original: {len(original)} chars, Corrected: {len(corrected)} chars")
                                    else:
                                        logger.info(f"Corrected code differs from original. Original: {len(original)} chars, Corrected: {len(corrected)} chars")
                                else:
                                    logger.info(f"Corrected code differs from original. Original: {len(original)} chars, Corrected: {len(corrected)} chars")
                            else:
                                logger.info(f"Corrected code differs from original and appears to fix errors. Original: {len(original)} chars, Corrected: {len(corrected)} chars")
                        
                        result["llm_explanation"] = llm_explanation
                    except Exception as e:
                        logger.error(f"Failed to generate LLM explanation: {e}", exc_info=True)
                        # Provide a basic fallback explanation
                        result["llm_explanation"] = {
                            "summary": "Analysis completed. Review errors below.",
                            "cause": f"LLM service error: {str(e)}",
                            "fix": "Fix the errors shown above and try again.",
                            "corrected_code": None
                        }
            else:
                # LLM service not available
                if not self.llm:
                    result["llm_explanation"] = {
                        "summary": "Analysis completed. Review errors below.",
                        "cause": "LLM service not initialized. Please check your GEMINI_API_KEY configuration in backend/.env file and restart the backend server.",
                        "fix": "To fix: 1) Verify GEMINI_API_KEY in backend/.env file, 2) Run 'python check_api_key.py' to diagnose, 3) Restart the backend server.",
                        "corrected_code": None
                    }
                else:
                    result["llm_explanation"] = {
                        "summary": "Analysis completed. Review errors below.",
                        "cause": "No errors detected that require AI explanation.",
                        "fix": "Fix the errors shown above and try again.",
                        "corrected_code": None
                    }
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}", exc_info=True)
            error_msg = str(e)
            result["compile_errors"] = {
                "success": False,
                "errors": [{
                    "line": 1,
                    "message": f"Analysis failed: {error_msg}",
                    "raw": error_msg
                }]
            }
            # Provide fallback LLM explanation
            result["llm_explanation"] = {
                "summary": "Analysis encountered an error.",
                "cause": error_msg,
                "fix": "Please check your code and try again. Ensure compilers (GCC/JDK) are installed.",
                "corrected_code": None
            }
        
        return result
    
    def _compile(self, language: str, code: str) -> Dict[str, Any]:
        """Compile code based on language."""
        if language == "C":
            return self.compiler.compile_c(code)
        elif language == "JAVA":
            return self.compiler.compile_java(code)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _execute(
        self,
        language: str,
        compile_result: Dict[str, Any],
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute compiled program based on language."""
        if language == "C":
            executable_path = compile_result.get("executable_path")
            if not executable_path:
                return {
                    "success": False,
                    "error": "Executable path not found"
                }
            return self.executor.execute_c(executable_path, input_data)
        
        elif language == "JAVA":
            class_path = compile_result.get("class_path")
            class_name = compile_result.get("class_name")
            if not class_path or not class_name:
                return {
                    "success": False,
                    "error": "Class path or name not found"
                }
            return self.executor.execute_java(class_path, class_name, input_data)
        
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _analyze_output(self, actual_output: str, expected_output: str) -> Dict[str, Any]:
        """Compare actual output with expected output."""
        # Handle None or empty inputs
        if actual_output is None:
            actual_output = ""
        if expected_output is None:
            expected_output = ""
        
        # Normalize outputs more aggressively
        # Remove all trailing whitespace and normalize line endings
        actual_normalized = actual_output.strip()
        expected_normalized = expected_output.strip()
        
        # Replace all types of line endings with single space, then strip again
        # This handles cases where output might have newlines but we want to compare as single value
        actual_normalized = ' '.join(actual_normalized.replace("\r\n", "\n").replace("\r", "\n").split())
        expected_normalized = ' '.join(expected_normalized.replace("\r\n", "\n").replace("\r", "\n").split())
        
        # Also try comparing line by line (in case user expects multiline output)
        actual_lines = [line.strip() for line in actual_output.replace("\r\n", "\n").replace("\r", "\n").split("\n") if line.strip()]
        expected_lines = [line.strip() for line in expected_output.replace("\r\n", "\n").replace("\r", "\n").split("\n") if line.strip()]
        
        # Check for exact match (single value comparison)
        match_single = actual_normalized == expected_normalized
        
        # Check for line-by-line match (multiline comparison)
        match_multiline = actual_lines == expected_lines
        
        # Smart matching: Check if expected output appears in actual output
        # This handles cases like:
        # - Actual: "Enter first number: Enter second number: Sum = 3"
        # - Expected: "3"
        match_contains = False
        if expected_normalized:
            # Check if expected output appears as a complete word/number in actual output
            # Use word boundaries for non-numeric, or check for number boundaries
            if expected_normalized.isdigit() or (expected_normalized.replace('.', '').replace('-', '').isdigit()):
                # For numeric values, check if it appears as a complete number
                # Pattern: number at start/end or surrounded by non-digit characters
                pattern = r'(^|\D)' + re.escape(expected_normalized) + r'(\D|$)'
                if re.search(pattern, actual_normalized):
                    match_contains = True
            else:
                # For non-numeric, check if it appears as a complete word
                pattern = r'\b' + re.escape(expected_normalized) + r'\b'
                if re.search(pattern, actual_normalized):
                    match_contains = True
                # Also check if expected appears in any line as complete word
                elif any(re.search(pattern, line) for line in actual_lines):
                    match_contains = True
        
        # Extract numeric values and compare (for cases like "Sum = 3" vs "3")
        match_numeric = False
        try:
            # Try to extract numbers from both outputs
            actual_numbers = re.findall(r'-?\d+\.?\d*', actual_normalized)
            expected_numbers = re.findall(r'-?\d+\.?\d*', expected_normalized)
            
            if expected_numbers:
                # If expected output contains a number, check if that number appears in actual output
                for exp_num in expected_numbers:
                    if exp_num in actual_numbers:
                        match_numeric = True
                        break
                    # Also check if the number appears as part of a larger string (e.g., "Sum = 3")
                    if exp_num in actual_normalized:
                        match_numeric = True
                        break
        except Exception:
            pass
        
        # Also check if both are empty (after normalization) - they should match
        if not actual_normalized and not expected_normalized:
            match = True
        else:
            # Match if any comparison succeeds
            match = match_single or match_multiline or match_contains or match_numeric
        
        # Use the original normalized values for display (preserve formatting)
        actual_display = actual_output.strip()
        expected_display = expected_output.strip()
        
        result = {
            "match": match,
            "expected": expected_display,
            "actual": actual_display,
            "status": "perfect" if match else "mismatch"
        }
        
        if not match:
            # Find differences
            difference = []
            max_len = max(len(actual_lines), len(expected_lines))
            
            for i in range(max_len):
                actual_line = actual_lines[i] if i < len(actual_lines) else None
                expected_line = expected_lines[i] if i < len(expected_lines) else None
                
                if actual_line != expected_line:
                    difference.append({
                        "line": i + 1,
                        "expected": expected_line,
                        "actual": actual_line
                    })
            
            result["difference"] = difference[:10]  # Limit to first 10 differences
            
            # Try to detect if it's a numeric/logical issue
            try:
                # Check if both are numeric (try both normalized and original)
                actual_num = float(actual_normalized.replace(',', '').replace(' ', ''))
                expected_num = float(expected_normalized.replace(',', '').replace(' ', ''))
                result["numeric_difference"] = expected_num - actual_num
                result["is_numeric"] = True
            except (ValueError, AttributeError):
                result["is_numeric"] = False
        
        return result

