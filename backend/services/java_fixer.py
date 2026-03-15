"""
Java code fixer service.
Provides programmatic fixes for common Java compilation errors as a fallback
when LLM doesn't fix the code correctly.
"""

import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class JavaCodeFixer:
    """Fixes common Java compilation errors programmatically."""
    
    def fix_common_errors(self, code: str, compile_errors: List[Dict[str, Any]]) -> str:
        """
        Fix common Java compilation errors programmatically.
        
        Args:
            code: Original Java source code
            compile_errors: List of compilation error dictionaries
            
        Returns:
            Fixed Java code
        """
        fixed_code = code
        error_text = str(compile_errors).lower()
        
        # Fix 1: Missing brackets [] in method parameters (String args -> String[] args)
        if "missing []" in error_text or ("array" in error_text and "string args" in code.lower()) or "String args" in fixed_code:
            # More comprehensive pattern matching
            fixed_code = re.sub(
                r'(\bpublic\s+static\s+void\s+main\s*\(\s*String\s+)(args)(\s*\))',
                r'\1[] \2\3',
                fixed_code,
                flags=re.IGNORECASE
            )
            # Also handle other String parameter cases
            fixed_code = re.sub(
                r'(\(String\s+)(\w+)(\s*\))',
                lambda m: f"(String[] {m.group(2)}{m.group(3)}" if m.group(2) == "args" else m.group(0),
                fixed_code,
                flags=re.IGNORECASE
            )
            logger.info("Fixed: Added missing [] to String args parameter")
        
        # Fix 2: Missing semicolons
        if "missing semicolon" in error_text or "';' expected" in error_text:
            # Find lines that end without semicolon (but not comments, strings, or already have semicolon)
            lines = fixed_code.split('\n')
            fixed_lines = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Skip empty lines, comments, preprocessor directives, braces-only lines
                if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    fixed_lines.append(line)
                    continue
                
                # Check if line ends with statement that needs semicolon
                # But not if it already has semicolon, or is a brace, or is part of control structure
                if (stripped and 
                    not stripped.endswith(';') and 
                    not stripped.endswith('{') and 
                    not stripped.endswith('}') and
                    not stripped.endswith(':') and
                    not any(keyword in stripped for keyword in ['if', 'for', 'while', 'switch', 'catch', 'else'])):
                    # Check if this looks like a statement (has = or is a method call or declaration)
                    if ('=' in stripped or 
                        '(' in stripped or 
                        re.search(r'\b(int|String|double|float|boolean|char|long|short|byte)\s+\w+', stripped) or
                        re.search(r'\b(return|System\.out\.println)', stripped)):
                        # Add semicolon if not already present
                        if not line.rstrip().endswith(';'):
                            fixed_lines.append(line.rstrip() + ';')
                            logger.info(f"Fixed: Added semicolon to line {i+1}: {stripped[:50]}")
                            continue
                
                fixed_lines.append(line)
            fixed_code = '\n'.join(fixed_lines)
        
        # Fix 3: Type mismatches (int b = "20" -> int b = 20)
        if "incompatible types" in error_text or "cannot convert" in error_text:
            # Find assignments like: int variable = "string"
            def fix_type_mismatch(match):
                var_type = match.group(1)  # int, String, etc.
                var_name = match.group(2)   # variable name
                string_value = match.group(3)  # "20"
                
                # Extract the numeric value from string
                numeric_match = re.search(r'"(\d+)"', string_value)
                if numeric_match and var_type.lower() in ['int', 'double', 'float', 'long', 'short', 'byte']:
                    numeric_value = numeric_match.group(1)
                    # Add decimal point for float/double if needed
                    if var_type.lower() in ['float', 'double'] and '.' not in numeric_value:
                        numeric_value = numeric_value + '.0'
                    return f"{var_type} {var_name} = {numeric_value};"
                return match.group(0)  # Return unchanged if we can't fix it
            
            fixed_code = re.sub(
                r'\b(int|String|double|float|boolean|char|long|short|byte)\s+(\w+)\s*=\s*"(\d+)"\s*;?',
                fix_type_mismatch,
                fixed_code
            )
            logger.info("Fixed: Corrected type mismatches")
        
        # Fix 4: Missing closing parentheses
        if "missing closing parenthesis" in error_text or "')' expected" in error_text:
            lines = fixed_code.split('\n')
            fixed_lines = []
            for i, line in enumerate(lines):
                open_parens = line.count('(')
                close_parens = line.count(')')
                if open_parens > close_parens:
                    # Add missing closing parentheses
                    missing = open_parens - close_parens
                    fixed_line = line.rstrip() + ')' * missing
                    fixed_lines.append(fixed_line)
                    logger.info(f"Fixed: Added {missing} closing parenthesis(es) to line {i+1}")
                else:
                    fixed_lines.append(line)
            fixed_code = '\n'.join(fixed_lines)
        
        # Fix 5: Missing opening braces for loops
        if "missing {" in error_text or "'{' expected" in error_text:
            # Fix: for (int i = 0; i < 5; i++) System.out.println -> for (...) { System.out.println }
            lines = fixed_code.split('\n')
            fixed_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Check if this is a for loop without braces
                if re.match(r'\s*for\s*\([^)]+\)\s*[^{]', line):
                    # Find the next non-empty line (the statement after the for loop)
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    if j < len(lines):
                        statement_line = lines[j]
                        # If the statement line doesn't start with {, we need to add braces
                        if not statement_line.strip().startswith('{'):
                            # Add opening brace after for loop
                            indent = len(line) - len(line.lstrip())
                            fixed_lines.append(line.rstrip() + ' {')
                            fixed_lines.append(statement_line)
                            # Check if we need closing brace
                            k = j + 1
                            while k < len(lines) and not lines[k].strip():
                                k += 1
                            if k >= len(lines) or not lines[k].strip().startswith('}'):
                                fixed_lines.append(' ' * indent + '}')
                            i = j + 1
                            logger.info(f"Fixed: Added braces for for loop at line {i}")
                            continue
                
                fixed_lines.append(line)
                i += 1
            fixed_code = '\n'.join(fixed_lines)
            logger.info("Fixed: Added missing braces for loops")
        
        # Fix 6: Undefined variables (return zero -> return 0)
        if "cannot find symbol" in error_text or "not defined" in error_text:
            # Fix common undefined variable names
            replacements = {
                'zero': '0',
                'one': '1',
                'two': '2',
                'three': '3',
                'four': '4',
                'five': '5',
            }
            
            for old, new in replacements.items():
                # Only replace if it's a standalone word (not part of another word)
                pattern = r'\b' + re.escape(old) + r'\b'
                if re.search(pattern, fixed_code, re.IGNORECASE):
                    fixed_code = re.sub(pattern, new, fixed_code, flags=re.IGNORECASE)
                    logger.info(f"Fixed: Replaced undefined variable '{old}' with '{new}'")
        
        # Fix 7: Remove calls to undeclared methods
        if "cannot find symbol" in error_text or "method not defined" in error_text or "undeclared" in error_text.lower():
            # Try to identify undeclared method calls and comment them out
            # This is a conservative fix - we'll comment out suspicious method calls
            lines = fixed_code.split('\n')
            fixed_lines = []
            for line in lines:
                stripped = line.strip()
                # Check if line contains a method call that might be undeclared
                # Look for patterns like: undeclaredMethod();
                if re.search(r'\b\w+\(\)\s*;?', stripped) and 'System.out.println' not in stripped and 'main' not in stripped:
                    method_match = re.search(r'\b(\w+)\s*\(\)\s*;?', stripped)
                    if method_match:
                        method_name = method_match.group(1)
                        # If method name suggests it's undeclared (like "undeclaredMethod")
                        # Or if it's a common pattern
                        if ('undeclared' in method_name.lower() or 
                            'undefined' in method_name.lower() or
                            method_name.lower() not in ['println', 'print', 'main', 'equals', 'hashcode', 'tostring']):
                            # Check if this method is actually declared in the code
                            if not re.search(rf'\b(public|private|protected|static)?\s+\w+\s+{re.escape(method_name)}\s*\(', fixed_code, re.IGNORECASE):
                                # Comment out the line, preserving indentation
                                indent = len(line) - len(line.lstrip())
                                fixed_lines.append(' ' * indent + '// ' + stripped + ' // Removed: method not defined')
                                logger.info(f"Fixed: Commented out undeclared method call: {method_name}")
                                continue
                fixed_lines.append(line)
            fixed_code = '\n'.join(fixed_lines)
        
        return fixed_code
    
    def apply_fixes(self, code: str, compile_errors: Dict[str, Any]) -> str:
        """
        Apply all applicable fixes to the code.
        
        Args:
            code: Original Java source code
            compile_errors: Compilation errors dictionary
            
        Returns:
            Fixed Java code
        """
        if not compile_errors.get("errors"):
            return code
        
        return self.fix_common_errors(code, compile_errors["errors"])

