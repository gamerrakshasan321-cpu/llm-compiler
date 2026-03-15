"""
LLM service for generating human-readable error explanations using Google Gemini API.
"""

import os
from typing import Dict, Any, Optional
import logging
import json
import warnings
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Explicitly load .env file from backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)
else:
    load_dotenv(override=True)

# Suppress deprecation warning for google.generativeai
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')

# Try new google.genai first, fallback to deprecated google.generativeai
try:
    import google.genai as genai_new
    USE_NEW_API = True
    genai = genai_new
    logger.info("Using google.genai (new API)")
except ImportError:
    try:
        import google.generativeai as genai
        USE_NEW_API = False
        logger.info("Using google.generativeai (will upgrade to google.genai in future)")
    except ImportError:
        genai = None
        USE_NEW_API = None
        logger.error("Neither google.genai nor google.generativeai is installed")


class LLMService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        self.use_new_api = False
        if genai is None:
            logger.error("Google Gemini API packages not available")
            self.model = None
            self.api_key = None
            self.client = None
            self.model_name = None
            return
            
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.model = None
            self.api_key = None
            self.client = None
            self.model_name = None
            return
        
        try:
            if USE_NEW_API:
                # New API: use Client (if available)
                try:
                    self.client = genai.Client(api_key=api_key)
                    # Use gemini-2.5-flash (latest available model)
                    self.model_name = 'models/gemini-2.5-flash'
                    logger.info("Using google.genai with gemini-2.5-flash model")
                    self.model = None  # Model is accessed via client in new API
                    self.use_new_api = True
                except Exception as e:
                    logger.warning(f"New API initialization failed: {e}, falling back to old API")
                    # Fallback to old API
                    try:
                        import google.generativeai as genai_old
                        genai_old.configure(api_key=api_key)
                        self.model = genai_old.GenerativeModel('gemini-pro')
                        logger.info("Using gemini-pro model (old API)")
                    except Exception as e2:
                        logger.error(f"Old API also failed: {e2}")
                        self.model = None
                    self.client = None
                    self.model_name = None
                    self.use_new_api = False
            else:
                # Old API: use configure (still works, just deprecated)
                try:
                    import google.generativeai as genai_old
                    genai_old.configure(api_key=api_key)
                    self.model = genai_old.GenerativeModel('gemini-pro')
                    logger.info("Using gemini-pro model (old API)")
                except Exception as e:
                    logger.warning(f"Failed to initialize old API model: {e}")
                    self.model = None
                self.client = None
                self.model_name = None
                self.use_new_api = False
            self.api_key = api_key
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}", exc_info=True)
            self.model = None
            self.client = None
            self.api_key = None
            self.model_name = None
            self.use_new_api = False
    
    def is_available(self) -> bool:
        """Check if LLM service is available and ready to use."""
        if self.use_new_api:
            return self.client is not None
        else:
            return self.model is not None
    
    def generate_explanation(
        self,
        language: str,
        code: str,
        compile_errors: Dict[str, Any],
        runtime_errors: Dict[str, Any],
        output_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate human-readable explanation using Gemini API.
        
        Args:
            language: Programming language (C or Java)
            code: Original source code
            compile_errors: Compilation error information
            runtime_errors: Runtime error information
            output_analysis: Output comparison analysis
            
        Returns:
            Dictionary with LLM-generated explanation
        """
        try:
            # Check if model/client is available
            if not self.is_available():
                error_msg = "LLM service not initialized. "
                if not self.api_key:
                    error_msg += "GEMINI_API_KEY not found in environment variables. "
                    error_msg += "Please check your .env file in the backend directory."
                elif self.use_new_api and not self.client:
                    error_msg += "Gemini client failed to initialize. "
                    error_msg += "Please check your GEMINI_API_KEY and restart the backend server."
                elif not self.use_new_api and not self.model:
                    error_msg += "Gemini model failed to initialize. "
                    error_msg += "Please check your GEMINI_API_KEY and restart the backend server."
                raise ValueError(error_msg)
            
            # Build prompt
            prompt = self._build_prompt(
                language, code, compile_errors, runtime_errors, output_analysis
            )
            
            # Generate response based on API version
            if self.use_new_api and self.client:
                # New API: use client.models.generate_content
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
                    # Extract text from new API response
                    response_text = None
                    if hasattr(response, 'text'):
                        response_text = response.text
                    elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content'):
                            if hasattr(candidate.content, 'parts'):
                                response_text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                            elif hasattr(candidate.content, 'text'):
                                response_text = candidate.content.text
                        elif hasattr(candidate, 'text'):
                            response_text = candidate.text
                    
                    if not response_text:
                        # Try to get text from response directly
                        response_text = str(response)
                        logger.warning(f"Could not extract text from response, using string representation")
                        
                except Exception as e:
                    logger.error(f"New API call failed: {e}", exc_info=True)
                    raise
            else:
                # Old API: use model.generate_content (still works, just deprecated)
                if not self.model:
                    raise ValueError("LLM model not initialized")
                    
                response = self.model.generate_content(prompt)
                
                # Extract text from response (handle different response formats)
                response_text = None
                if hasattr(response, 'text'):
                    response_text = response.text
                elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content'):
                        if hasattr(candidate.content, 'parts'):
                            response_text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                        elif hasattr(candidate.content, 'text'):
                            response_text = candidate.content.text
                    elif hasattr(candidate, 'text'):
                        response_text = candidate.text
            
            if not response_text:
                logger.error(f"No text content in LLM response. Response object: {response}")
                raise ValueError("No text content in LLM response")
            
            logger.info(f"LLM response received, length: {len(response_text)} characters")
            
            with open("raw_llm_response.txt", "w", encoding="utf-8") as raw_f:
                raw_f.write(response_text)
            
            # Log the full response for debugging (first 3000 chars)
            logger.info(f"LLM response preview: {response_text[:3000]}")
            
            # Parse response
            explanation = self._parse_response(response_text)
            
            # Validate that we have explanations for all errors
            if compile_errors.get("errors") and explanation.get("cause"):
                num_errors = len(compile_errors["errors"])
                cause_text = explanation["cause"]
                
                # Count explanation points (lines starting with • or Line or numbers)
                import re
                explanation_points = re.findall(r'(?:^|\n)(?:•|Line\s*\d+:|^\d+\.|-\s+|[*]\s+)', cause_text, re.MULTILINE)
                num_explanations = len(explanation_points)
                
                logger.info(f"Found {num_errors} errors, {num_explanations} explanation points in response")
                
                if num_explanations < num_errors:
                    logger.warning(f"WARNING: Only {num_explanations} explanation points found for {num_errors} errors. Some explanations may be missing!")
                    # Try to extract more explanation points from the response
                    # Look for any line that mentions a line number
                    line_mentions = re.findall(r'Line\s+\d+', cause_text, re.IGNORECASE)
                    logger.debug(f"Found {len(line_mentions)} line number mentions in explanation")
            
            # Log parsed explanation to verify completeness
            if explanation.get("cause"):
                cause_lines = [l for l in explanation["cause"].split('\n') if l.strip()]
                logger.info(f"Parsed explanation has {len(cause_lines)} non-empty lines in cause field")
                logger.debug(f"Cause preview (first 1000 chars): {explanation['cause'][:1000]}")
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating LLM explanation: {e}", exc_info=True)
            # Return fallback explanation with more context
            error_msg = str(e).lower()
            
            # Provide a helpful fallback based on error type
            if "not initialized" in error_msg or "api_key" in error_msg or "gemini_api_key" in error_msg:
                cause_msg = "LLM service not initialized. Please check your GEMINI_API_KEY configuration in the backend/.env file and restart the backend server."
            elif "api key" in error_msg or "invalid" in error_msg or "401" in error_msg or "403" in error_msg:
                cause_msg = "Invalid or unauthorized API key. Please verify your GEMINI_API_KEY at https://makersuite.google.com/app/apikey and restart the backend server."
            elif "quota" in error_msg or "429" in error_msg:
                cause_msg = "API quota exceeded. Please check your Gemini API usage limits."
            elif "timeout" in error_msg:
                cause_msg = "Request timed out. The LLM service took too long to respond. Please try again."
            elif "network" in error_msg or "connection" in error_msg:
                cause_msg = "Network error. Please check your internet connection and try again."
            else:
                cause_msg = f"LLM service error: {str(e)}. Please check backend logs for details."
            
            return {
                "summary": "Unable to generate AI explanation. Please review the error messages below.",
                "cause": cause_msg,
                "fix": "To fix: 1) Verify GEMINI_API_KEY in backend/.env file, 2) Run 'python check_api_key.py' to diagnose, 3) Restart the backend server. Check the compilation errors above and review your code.",
                "corrected_code": None
            }
    
    def _build_prompt(
        self,
        language: str,
        code: str,
        compile_errors: Dict[str, Any],
        runtime_errors: Dict[str, Any],
        output_analysis: Dict[str, Any]
    ) -> str:
        """Build the prompt for the LLM."""
        
        prompt = f"""You are an expert {language} programming tutor. Analyze the following code and errors, then provide a clear, structured, point-by-point explanation.

**STRICT RULES:**
1. Only explain the errors listed in the compiler output.
2. Do NOT invent errors that are not mentioned in the compiler output.
3. Do NOT repeat the same error more than once.
4. Use the exact line numbers from the compiler output.
5. If multiple compiler errors are caused by one earlier mistake, identify it as the ROOT ERROR and explain that later errors are cascading errors.
6. Keep explanations simple and beginner-friendly.
7. When suggesting fixes, only modify the specific line that caused the error.
8. After explaining all errors, generate the fully corrected program.

**ANALYSIS PROCESS:**
Step 1: Read the program carefully.
Step 2: Read the compiler error messages.
Step 3: Match each compiler error to the corresponding line in the code.
Step 4: Explain the error and provide the corrected line.

**Source Code ({language}):**
```
{code}
```

**Reported Compilation Errors (Compiler Output):**
"""
        
        compile_error_list = []
        if compile_errors.get("errors") and len(compile_errors["errors"]) > 0:
            code_lines = code.split('\n')
            seen_lines = set() # Track lines we've already included to avoid duplicates
            
            for idx, error in enumerate(compile_errors["errors"]):
                if isinstance(error, dict):
                    line = error.get("line")
                    msg = error.get("message", error.get("raw", str(error)))
                    
                    if line is None:
                        line_match = re.search(r'line\s+(\d+)|:(\d+):', str(msg), re.IGNORECASE)
                        if line_match:
                            line = int(line_match.group(1) or line_match.group(2))
                        else:
                            line = idx + 1
                    
                    if line in seen_lines:
                        continue
                    seen_lines.add(line)
                    
                    code_line = ""
                    if line and 1 <= line <= len(code_lines):
                        code_line = code_lines[line - 1].strip()
                    
                    if code_line:
                        compile_error_list.append({"line": line, "message": msg, "code": code_line})
                        prompt += f"Line {line}: {msg}\n   Code snippet: {code_line}\n"
                    else:
                        compile_error_list.append({"line": line, "message": msg, "code": ""})
                        prompt += f"Line {line}: {msg}\n"
                else:
                    compile_error_list.append({"line": idx + 1, "message": str(error), "code": ""})
                    prompt += f"{str(error)}\n"
            
            prompt += f"\nNote: The compiler stopped early. Analyze the whole file for more issues.\n"
        else:
            prompt += "None (compilation successful)\n"
        
        prompt += "\n**Runtime Errors:**\n"
        if runtime_errors and not runtime_errors.get("success"):
            error_msg = runtime_errors.get('error', runtime_errors.get('stderr', 'Unknown runtime error'))
            prompt += f"Error: {error_msg}\n"
        else:
            prompt += "None\n"
        
        prompt += "\n**Output Analysis:**\n"
        if output_analysis.get("match") is True:
            prompt += "✓ Output matches expected result.\n"
        elif output_analysis.get("match") is False:
            prompt += "✗ Output MISMATCH.\n"
            if output_analysis.get("expected"):
                prompt += f"Expected: {output_analysis['expected']}\n"
            if output_analysis.get("actual"):
                prompt += f"Actual: {output_analysis['actual']}\n"
        else:
            prompt += "No comparison data.\n"
        
        prompt += f"""
**Your Task:**
Return a JSON object with this exact structure:
{{
  "section_root_cause": "Explain the main syntax mistake that caused the compilation to fail.",
  "all_errors": [
    {{
      "line": 10,
      "compiler_message": "Exact message from compiler output",
      "explanation": "Clear beginner-friendly explanation",
      "fix": "Corrected version of ONLY that line"
    }}
  ],
  "corrected_code": "Complete valid {language} code fixing all issues."
}}

**Important Constraints:**
- Think step-by-step like a C compiler parser before generating the explanation.
- Do not repeat errors.
- If multiple errors share the exact same cause, do not repeat the full explanation. Just mention it once or refer to the previous line.
- Do not invent errors that do not exist.
- Do not show the entire corrected program inside each fix.
- Only show the corrected line for each error.
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format."""
        try:
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            text = response_text.strip()
            
            # Look for JSON code blocks
            if "```json" in text.lower():
                # Extract JSON from ```json ... ``` block
                parts = text.split("```json")
                if len(parts) > 1:
                    text = parts[1].split("```")[0].strip()
            elif "```" in text:
                # Extract from generic code block
                parts = text.split("```")
                if len(parts) > 1:
                    text = parts[1].split("```")[0].strip()
            
            # Try to find JSON object in the text - use a more robust pattern that handles nested structures
            import re
            # Try to find the JSON object by finding the first '{' and last '}'
            json_start = text.find('{')
            json_end = text.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                text = text[json_start:json_end+1]
            
            # Parse JSON - handle potential parsing errors
            try:
                explanation = json.loads(text, strict=False)
            except json.JSONDecodeError:
                # Try to clean up text more aggressively
                # Remove common LLM chatter at the end of JSON
                text = re.sub(r'\}\s*[^}]*$', '}', text)
                try:
                    explanation = json.loads(text, strict=False)
                except json.JSONDecodeError:
                    raise
            
            # Ensure all required fields and extract corrected_code properly
            corrected_code = explanation.get("corrected_code")
            
            # Handle null or empty corrected_code
            if not corrected_code or corrected_code == "null" or corrected_code.lower() == "none":
                # Try to generate corrected code from the original code and errors
                logger.warning("LLM returned null/empty corrected_code, attempting to extract from fix field")
                fix_text = explanation.get("fix", "")
                # If fix contains code blocks, extract them
                if "```" in fix_text:
                    import re
                    code_blocks = re.findall(r'```(?:c|java|C|JAVA)?\n?(.*?)```', fix_text, re.DOTALL)
                    if code_blocks:
                        corrected_code = code_blocks[-1].strip()
                # If still no code, don't use original as fallback - return None so frontend can handle
                if not corrected_code or corrected_code == "null":
                    corrected_code = None
            
            if corrected_code and isinstance(corrected_code, str):
                # Remove code block markers if present
                corrected_code = corrected_code.strip()
                if corrected_code.startswith("```"):
                    corrected_code = corrected_code.split("```")[1]
                    if "\n" in corrected_code:
                        corrected_code = corrected_code.split("\n", 1)[1]
                    corrected_code = corrected_code.rsplit("```", 1)[0].strip()
                # Unescape JSON string escapes
                corrected_code = corrected_code.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                
                # Note: Validation that corrected_code differs from original is done in analyzer.py
                # where we have access to both the original code and the LLM response
            
            # Clean up the cause field - remove JSON artifacts and format properly
            cause = explanation.get("cause", "No cause analysis provided")
            
            # Ensure cause is a string
            if not isinstance(cause, str):
                if isinstance(cause, (dict, list)):
                    try:
                        cause = json.dumps(cause, indent=2)
                    except:
                        cause = str(cause)
                else:
                    cause = str(cause)
            
            if isinstance(cause, str):
                # Remove JSON formatting artifacts
                cause = cause.strip()
                # Remove markdown code blocks if present
                if "```" in cause:
                    # Remove all code blocks
                    cause = re.sub(r'```json\s*', '', cause, flags=re.IGNORECASE)
                    cause = re.sub(r'```\s*', '', cause)
                # Remove JSON structure artifacts (opening/closing braces, brackets)
                cause = re.sub(r'^\s*\{[\s\n]*', '', cause)
                cause = re.sub(r'[\s\n]*\}\s*$', '', cause)
                cause = re.sub(r'^\s*\[[\s\n]*', '', cause)
                cause = re.sub(r'[\s\n]*\]\s*$', '', cause)
                # Remove JSON field markers if they appear in the text
                cause = re.sub(r'^\s*"cause"\s*:\s*', '', cause, flags=re.IGNORECASE)
                cause = re.sub(r'^\s*"summary"\s*:\s*', '', cause, flags=re.IGNORECASE)
                # Remove trailing commas and standalone JSON punctuation
                cause = re.sub(r',\s*$', '', cause)
                # Remove lines that are just JSON punctuation
                lines = cause.split('\n')
                cleaned_lines = []
                for line in lines:
                    trimmed = line.strip()
                    # Skip lines that are just JSON artifacts
                    if trimmed and trimmed not in [',', ']', '}', '[', '{', '},', '],']:
                        cleaned_lines.append(line)
                cause = '\n'.join(cleaned_lines)
                # Unescape JSON string escapes
                cause = cause.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                cause = cause.strip()
            
            # Construct cause string from all_errors if available
            all_errors = explanation.get("all_errors", [])
            if isinstance(all_errors, list) and len(all_errors) > 0:
                new_cause = ""
                # Sort errors by line number
                try:
                    all_errors.sort(key=lambda x: int(x.get("line", 0)) if isinstance(x, dict) else 0)
                except:
                    pass
                
                for err in all_errors:
                    if isinstance(err, dict):
                        line = err.get("line", "?")
                        msg = err.get("message", "Error")
                        exp = err.get("explanation", "")
                        
                        # Format: • Line X: [Message] - [Explanation]
                        if exp:
                            new_cause += f"• Line {line}: {msg} - {exp}\n"
                        else:
                            new_cause += f"• Line {line}: {msg}\n"
                
                if new_cause:
                    cause = new_cause.strip()

            return {
                "summary": explanation.get("section_root_cause", explanation.get("summary", "No summary provided")),
                "section_root_cause": explanation.get("section_root_cause", ""),
                "cause": cause,
                "all_errors": all_errors,
                "fix": explanation.get("fix", "No fix suggestions provided"),
                "corrected_code": corrected_code
            }
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract information manually
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            
            import re
            
            # Try to extract fields from the text even if not valid JSON
            summary = None
            cause = None
            fix = None
            corrected_code = None
            
            # Try to find JSON-like structure in the text
            # Look for "summary": "..." or "cause": "..." patterns
            summary_match = re.search(r'"summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if summary_match:
                summary = summary_match.group(1).replace('\\n', '\n').replace('\\"', '"')
            
            # Try to extract cause field - handle long multi-line content
            # Pattern 1: Standard JSON string (handles escaped quotes and newlines)
            cause_match = re.search(r'"cause"\s*:\s*"((?:[^"\\]|\\.|\\n)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if not cause_match:
                # Pattern 2: Multi-line cause that might span multiple lines
                # Look for "cause": followed by content until next field or end of object
                cause_match = re.search(r'"cause"\s*:\s*"((?:[^"]|\\"|\\n)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if not cause_match:
                # Pattern 3: Try to find cause field even if JSON is malformed
                # Look for content between "cause": and next field or closing brace
                cause_match = re.search(r'"cause"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if cause_match:
                cause = cause_match.group(1).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                # Clean up any remaining escape sequences
                cause = cause.replace('\\t', '\t').replace('\\r', '\r')
            
            fix_match = re.search(r'"fix"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if not fix_match:
                # Try multiline fix
                fix_match = re.search(r'"fix"\s*:\s*"((?:[^"\\]|\\.|\\n)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if fix_match:
                fix = fix_match.group(1).replace('\\n', '\n').replace('\\"', '"')
            
            # Try to find corrected_code field - handle both JSON string format and code blocks
            # First try JSON format
            corrected_code_match = re.search(r'"corrected_code"\s*:\s*"((?:[^"\\]|\\.|\\n)*)"', response_text, re.IGNORECASE | re.DOTALL)
            if corrected_code_match:
                corrected_code = corrected_code_match.group(1).replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            
            # If not found in JSON, try to find code blocks in the response
            if not corrected_code or corrected_code.lower() in ['null', 'none', '']:
                code_blocks = re.findall(r'```(?:c|java|C|JAVA)?\n?(.*?)```', response_text, re.DOTALL)
                if code_blocks:
                    # Use the last/largest code block as corrected code
                    corrected_code = max(code_blocks, key=len).strip()
            
            # If still no corrected_code found, try to extract from fix field if it contains code
            if (not corrected_code or corrected_code.lower() in ['null', 'none', '']) and fix:
                fix_code_blocks = re.findall(r'```(?:c|java|C|JAVA)?\n?(.*?)```', fix, re.DOTALL)
                if fix_code_blocks:
                    corrected_code = max(fix_code_blocks, key=len).strip()
                elif fix and (fix.count('\n') > 5 or '#include' in fix or 'public class' in fix or 'class ' in fix):
                    # Fix text itself might be code
                    corrected_code = fix.strip()
            
            # If we still don't have cause, try to extract from the response text directly
            if not cause:
                # Look for explanation-like text after "cause" or "explanation" keywords
                # Try to find a larger section that might contain the full explanation
                cause_section = re.search(r'(?:cause|explanation)[\s:]*["\']?([^"\']{50,2000})', response_text, re.IGNORECASE | re.DOTALL)
                if cause_section:
                    cause = cause_section.group(1).strip()
                else:
                    # Use a larger portion of the response as cause - don't limit to 10 lines
                    lines = response_text.split('\n')
                    # Skip lines that look like JSON structure
                    meaningful_lines = [l for l in lines if l.strip() and not l.strip().startswith('{') and not l.strip().startswith('}') and not l.strip().startswith('"') and not l.strip().startswith('```')]
                    if meaningful_lines:
                        # Take all meaningful lines, not just first 10
                        cause = '\n'.join(meaningful_lines)
            
            # Fallback values
            if not summary:
                summary = response_text[:200] if response_text else "Explanation generated"
            if not cause:
                # Try to use the full response as cause - don't truncate
                # Remove JSON structure markers first
                cleaned_response = response_text
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response, flags=re.IGNORECASE)
                cleaned_response = re.sub(r'```\s*', '', cleaned_response)
                cleaned_response = re.sub(r'^\s*\{[\s\n]*', '', cleaned_response)
                cleaned_response = re.sub(r'[\s\n]*\}\s*$', '', cleaned_response)
                cause = cleaned_response.strip()
            if not fix:
                fix = "Please review the error messages and code carefully"
                
            # If we still have a very generic cause, try to look for bullet points in the whole response
            if cause and len(cause.split('\n')) < 2 and response_text.count('•') > 1:
                bullet_points = re.findall(r'(?:•|Line\s*\d+:|^\d+\.).*', response_text, re.MULTILINE)
                if bullet_points:
                    cause = '\n'.join(bullet_points).strip()
            
            # Try to find corrected code in code blocks
            code_blocks = re.findall(r'```(?:c|java)?\n?(.*?)```', response_text, re.DOTALL)
            if code_blocks and not corrected_code:
                corrected_code = code_blocks[-1].strip()
            
            return {
                "summary": summary,
                "summary_of_errors": "",
                "cause": cause,
                "fix": fix,
                "all_errors": [],
                "corrected_code": corrected_code
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}", exc_info=True)
            return {
                "summary": response_text[:200] if response_text else "Explanation generated",
                "cause": "Error parsing LLM response",
                "fix": "Please review the error messages and code carefully",
                "corrected_code": None
            }

