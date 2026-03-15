import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Play, RotateCcw, Moon, Sun, Sparkles, AlertTriangle } from "lucide-react";
import CodeEditor from "./CodeEditor";
import LanguageSelector from "./LanguageSelector";
import TestCaseInput from "./TestCaseInput";
import ResultsPanel from "./ResultsPanel";
import { toast } from "sonner";

// API endpoint - adjust if backend is on different port
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Empty starter code templates
const emptyCode = {
  C: `#include <stdio.h>

int main() {
    // Write your C code here
    
    return 0;
}`,
  Java: `public class Main {
    public static void main(String[] args) {
        // Write your Java code here
    }
}`,
};

interface AnalysisResult {
  compileErrors: Array<{
    line: number;
    message: string;
    code: string;
    explanation: string;
    suggestion: string;
    compilerMessage?: string;
    fix?: string;
    hasCorrectedCode?: boolean;
  }>;
  runtimeErrors: Array<{
    type: string;
    message: string;
    stackTrace: string[];
    explanation: string;
    suggestion: string;
    hasCorrectedCode?: boolean;
  }>;
  outputMismatch: {
    expected: string;
    actual: string;
    explanation: string;
  } | null;
  aiExplanations: string[];
  executionSuccess?: boolean;
  programOutput?: string;
  sectionRootCause?: string;
  cascadingErrors?: string;
  logicalErrorCorrectedCode?: string | null;
  compileErrorCorrectedCode?: string | null;
  expectedOutput?: string | null;
  inputData?: string | null;
}

const Workspace = () => {
  const [language, setLanguage] = useState<'C' | 'Java'>('C');
  const [code, setCode] = useState(emptyCode.C);
  const [inputData, setInputData] = useState('');
  const [expectedOutput, setExpectedOutput] = useState('');
  const [isDark, setIsDark] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [llmStatus, setLlmStatus] = useState<{available: boolean; message: string; setup_guide?: any} | null>(null);

  // Set dark mode on mount
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Check LLM status on mount
  useEffect(() => {
    const checkLlmStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/llm/status`);
        if (response.ok) {
          const status = await response.json();
          setLlmStatus(status);
        }
      } catch (error) {
        // Backend might not be running, that's okay
        console.log("Could not check LLM status - backend may not be running");
      }
    };
    checkLlmStatus();
  }, []);

  const handleLanguageChange = (newLanguage: 'C' | 'Java') => {
    setLanguage(newLanguage);
    setCode(emptyCode[newLanguage]);
    setResults(null);
  };

  // Helper function to extract corrected code from JSON string if needed
  const extractCorrectedCode = (codeOrJson: string): string => {
    if (!codeOrJson) return codeOrJson;
    
    const trimmed = codeOrJson.trim();
    
    // Try to parse as JSON first
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed && typeof parsed === 'object') {
        // If it's a JSON object, extract corrected_code field
        if (parsed.corrected_code) {
          let code = parsed.corrected_code;
          // Handle null case
          if (code === null || code === undefined) {
            return '';
          }
          // If it's a string, unescape it
          if (typeof code === 'string') {
            return code.replace(/\\n/g, '\n').replace(/\\"/g, '"').replace(/\\\\/g, '\\');
          }
          return String(code);
        }
      }
    } catch (e) {
      // Not valid JSON, continue to other methods
    }
    
    // Check if it contains JSON structure with corrected_code field
    // Pattern: "corrected_code": "code here" or "corrected_code": "code\nhere"
    const jsonFieldMatch = trimmed.match(/"corrected_code"\s*:\s*"((?:[^"\\]|\\.)*)"/s);
    if (jsonFieldMatch) {
      // Unescape the string (handle \n, \", etc.)
      return jsonFieldMatch[1]
        .replace(/\\n/g, '\n')
        .replace(/\\"/g, '"')
        .replace(/\\\\/g, '\\')
        .replace(/\\t/g, '\t')
        .replace(/\\r/g, '\r');
    }
    
    // Check for code blocks (```c or ```java)
    if (trimmed.includes('```')) {
      const codeBlockMatch = trimmed.match(/```(?:c|java|C|JAVA)?\n?(.*?)```/s);
      if (codeBlockMatch) {
        return codeBlockMatch[1].trim();
      }
    }
    
    // If it starts with #include or public class, it's likely already code
    if (trimmed.startsWith('#include') || trimmed.startsWith('public class')) {
      return trimmed;
    }
    
    // Return as-is if no JSON detected
    return trimmed;
  };

  const transformBackendResponse = (backendData: any): AnalysisResult => {
    const compileErrors: AnalysisResult['compileErrors'] = [];
    const runtimeErrors: AnalysisResult['runtimeErrors'] = [];
    let outputMismatch: AnalysisResult['outputMismatch'] = null;

    // Transform compile errors
    if (backendData.compile_errors && !backendData.compile_errors.success) {
      const errors = backendData.compile_errors.errors || [];
      let summaryUsedAsFallbackCount = 0; // Track how many times we use the summary fallback
      const seenExplanations = new Set<string>(); // Keep track of explanations to prevent duplicates
      const seenLines = new Set<number>(); // Track lines to prevent multiple errors on the same line
      
      errors.forEach((error: any, index: number) => {
        // Handle both string and object error formats
        let errorLine: number | null = null;
        let errorMessage = '';
        
        if (typeof error === 'object' && error !== null) {
          errorLine = error.line || null;
          errorMessage = error.message || error.raw || JSON.stringify(error);
        } else {
          errorMessage = String(error);
          // Try to extract line number from error message
          const lineMatch = errorMessage.match(/line\s+(\d+)/i) || 
                          errorMessage.match(/:(\d+):/) ||
                          errorMessage.match(/\.java:(\d+):/) ||
                          errorMessage.match(/\.c:(\d+):/);
          if (lineMatch) {
            errorLine = parseInt(lineMatch[1]);
          }
        }
        
        const line = errorLine || index + 1;
        
        // Skip if we already have an error for this line
        if (seenLines.has(line)) {
          return;
        }
        seenLines.add(line);
        
        // Extract code snippet around the error
        const codeLines = code.split('\n');
        const codeSnippet = codeLines[line - 1] || codeLines[0] || '';
        
        // Extract just the error message without file path
        const cleanMessage = errorMessage.split(':').slice(-1)[0]?.trim() || errorMessage;
        
        // Get corrected code from LLM explanation, or use fix instructions
        let suggestion = codeSnippet.trim();
        let hasCorrectedCode = false;
        
        // First try to get corrected_code
        if (backendData.llm_explanation?.corrected_code) {
          const extractedCode = extractCorrectedCode(backendData.llm_explanation.corrected_code);
          if (extractedCode && extractedCode.trim().length > 0 && extractedCode.toLowerCase() !== 'null') {
            suggestion = extractedCode;
            // Check if it looks like complete code
            hasCorrectedCode = extractedCode.includes('#include') || 
                              extractedCode.includes('public class') || 
                              extractedCode.includes('class ') ||
                              extractedCode.split('\n').length > 3 ||
                              extractedCode.length > 100;
          }
        }
        
        // If no corrected_code, try to extract from fix field
        // BUT: Skip if fix contains LLM setup instructions (don't show setup instructions as corrected code)
        if (!hasCorrectedCode && backendData.llm_explanation?.fix) {
          const fixText = backendData.llm_explanation.fix;
          // Check if fix is LLM setup instructions (contains "GEMINI_API_KEY", "check_api_key.py", "restart", etc.)
          const isSetupInstructions = /GEMINI_API_KEY|check_api_key\.py|restart.*server|setup.*guide|api.*key|configuration/i.test(fixText);
          
          if (!isSetupInstructions) {
            // Check if fix contains code blocks
            if (fixText.includes('```')) {
              const codeMatch = fixText.match(/```(?:c|java|C|JAVA)?\n?(.*?)```/s);
              if (codeMatch && codeMatch[1].trim().length > 0) {
                suggestion = codeMatch[1].trim();
                hasCorrectedCode = suggestion.includes('#include') || 
                                  suggestion.includes('public class') || 
                                  suggestion.includes('class ') ||
                                  suggestion.split('\n').length > 3;
              }
            } else if (fixText.includes('#include') || fixText.includes('public class') || fixText.split('\n').length > 5) {
              // Fix text itself might be code
              suggestion = fixText;
              hasCorrectedCode = true;
            } else if (fixText.length > 200 || fixText.split('\n').length > 10) {
              // Long fix text might contain code snippets
              suggestion = fixText;
            }
          }
        }
        
        // Fallback: if still no suggestion, try to use the original code as base
        // BUT: Don't use setup instructions or generic messages as suggestion
        if (!suggestion || suggestion.trim().length === 0 || suggestion === codeSnippet.trim() || 
            suggestion.toLowerCase().includes('no fix') ||
            /GEMINI_API_KEY|check_api_key\.py|restart.*server|setup.*guide/i.test(suggestion)) {
          // If we have the full code, use it as a starting point
          if (code && code.trim().length > 0) {
            suggestion = code;
          } else {
            // Don't show generic messages - just show error code snippet
            suggestion = codeSnippet.trim() || "Please review the error message and fix the code accordingly.";
          }
        }
        
        // Get explanation - extract the specific point for this compile-time error's line number
        // IMPORTANT: Only look for compile-time error explanations (those starting with "Line X:")
        let explanation = "";
        const fullExplanation = backendData.llm_explanation?.cause || "";
        
        if (fullExplanation) {
          // Clean up explanation - remove JSON artifacts
          let cleanedExplanation = fullExplanation
            .replace(/```json\s*/gi, '')
            .replace(/```\s*/g, '')
            .replace(/^[\s\n]*\{[\s\n]*/g, '')
            .replace(/[\s\n]*\}[\s\n]*$/g, '')
            .replace(/^[\s\n]*\[[\s\n]*/g, '')
            .replace(/[\s\n]*\][\s\n]*$/g, '')
            .replace(/^\s*"cause"\s*:\s*/gi, '')
            .replace(/^\s*"summary"\s*:\s*/gi, '')
            .replace(/,\s*$/, '')
            .trim();
          
          // Split explanation into lines and filter for compile-time error explanations only
          // Compile-time errors start with "Line X:" or "• Line X:" etc.
          // Runtime errors start with "Runtime Error:" or "Runtime:" - ignore those here
          const lines = cleanedExplanation.split('\n');
          
          // Find ALL explanation points with line numbers first
          const allLineExplanations: Array<{lineNum: number, explanation: string, index: number}> = [];
          for (let i = 0; i < lines.length; i++) {
            const trimmed = lines[i].trim();
            // Skip runtime error explanations - they start with "Runtime"
            if (trimmed.match(/^(?:•|\d+\.|[-*])?\s*Runtime\s*Error?:/i)) {
              continue;
            }
            // Check if this line mentions a line number (compile-time error)
            const lineMatch = trimmed.match(/^(?:•|\d+\.|[-*])\s*Line\s+(\d+):/i) || 
                            trimmed.match(/^Line\s+(\d+):/i);
            if (lineMatch) {
              const expLineNum = parseInt(lineMatch[1]);
              // Extract explanation for this line
              let extractedExplanation = trimmed.replace(/^(?:•|\d+\.|[-*])\s*Line\s+\d+:\s*/i, '')
                                                 .replace(/^Line\s+\d+:\s*/i, '')
                                                 .trim();
              
              // Collect continuation lines (lines that don't start with bullet, number, or "Line X:")
              for (let j = i + 1; j < lines.length; j++) {
                const nextLine = lines[j].trim();
                // Stop if we hit another bullet point, line number, or runtime error
                if (!nextLine || 
                    /^(?:•|\d+\.|[-*])\s*Line\s+\d+:/i.test(nextLine) ||
                    /^(?:•|\d+\.|[-*])\s*Runtime\s*Error?:/i.test(nextLine) ||
                    (/^\d+\./.test(nextLine) && nextLine.length < 10)) {
                  break;
                }
                // Add continuation line if it's not empty
                if (nextLine && nextLine !== ',' && nextLine !== ']' && nextLine !== '}') {
                  extractedExplanation += ' ' + nextLine;
                }
              }
              
              allLineExplanations.push({
                lineNum: expLineNum,
                explanation: extractedExplanation.trim(),
                index: i
              });
            }
          }
          
          // Now find the explanation for the current error's line number
          const matchingExplanation = allLineExplanations.find(exp => exp.lineNum === line);
          if (matchingExplanation) {
            explanation = matchingExplanation.explanation;
          } else if (allLineExplanations.length > 0 && index < allLineExplanations.length) {
            // Fallback: use explanation at the same index as the error
            explanation = allLineExplanations[index].explanation;
          }
          
          // If still no explanation found after matching by line number, try index-based fallback
          if (!explanation && allLineExplanations.length > 0) {
            // If we have explanations but none matched by line number, use index-based matching
            if (index < allLineExplanations.length) {
              explanation = allLineExplanations[index].explanation;
            } else if (allLineExplanations.length === 1) {
              // Only one explanation available, use it for all errors
              explanation = allLineExplanations[0].explanation;
            }
          }
        }
        
        // Fallback: if still no explanation, use summary or create a simple one
        if (!explanation || explanation.trim().length < 10) {
          if (summaryUsedAsFallbackCount === 0) {
            explanation = backendData.llm_explanation?.summary || "";
            if (explanation) {
              explanation = explanation.replace(/```json\s*/gi, '').replace(/```\s*/g, '');
              explanation = explanation.replace(/^[\s\n]*\{[\s\n]*/g, '').replace(/[\s\n]*\}[\s\n]*$/g, '');
              explanation = explanation.trim();
              summaryUsedAsFallbackCount++;
            }
          } else {
             // Don't repeat the summary for subsequent errors
             explanation = ""; 
          }
        }
        
        // Final fallback: create a simple explanation with line number and error description
        if (!explanation || explanation.trim().length < 10) {
          // Create a simple explanation without "What is the error:" and "How to resolve:" structure
          explanation = `Line ${line}: ${cleanMessage}. Please review the error message and fix the code accordingly.`;
        } else {
          // Remove "What is the error:" and "How to resolve:" prefixes if present
          explanation = explanation
            .replace(/^(?:What is the error|Error|Issue|Problem)[:\s]+/gi, '')
            .replace(/^(?:How to resolve|Resolution|Fix|Solution|How to fix|How to correct)[:\s]+/gi, '')
            .replace(/\n\n(?:What is the error|Error|Issue|Problem)[:\s]+/gi, '\n\n')
            .replace(/\n\n(?:How to resolve|Resolution|Fix|Solution|How to fix|How to correct)[:\s]+/gi, '\n\n')
            .trim();
          
          // Ensure explanation includes line number if not already present
          if (!explanation.includes(`Line ${line}`) && !explanation.includes(`line ${line}`) && !explanation.startsWith(`${line}:`)) {
            explanation = `Line ${line}: ${explanation}`;
          }
        }
        
        let compilerMessage = "";
        let specificFix = "";
        const allErrors = backendData.llm_explanation?.all_errors || [];
        const matchedError = allErrors.find((e: any) => e.line === line) || 
                             (index < allErrors.length ? allErrors[index] : null);
        if (matchedError) {
            compilerMessage = matchedError.compiler_message || "";
            specificFix = matchedError.fix || "";
            if (!explanation || explanation.includes("Please review") || explanation.includes("Error at line") || explanation.includes("Line ")) {
                 explanation = matchedError.explanation || explanation;
            }
        }
        
        // Don't truncate explanation - show full explanation for each error
        // Users need to see all details to understand and fix the error
        
        // Prevent duplicate explanations
        if (explanation && explanation.trim().length > 10) {
          const normExp = explanation.toLowerCase().replace(/[^\w\s]/g, '');
          if (seenExplanations.has(normExp)) {
            // Already seen this exact explanation, replace with a simple generic one
            explanation = `Line ${line}: ${cleanMessage}. Please review the error message and fix the code accordingly.`;
          } else {
            seenExplanations.add(normExp);
          }
        }
        
        // Debug: Log error processing (remove in production)
        console.log(`Processing error ${index + 1}/${errors.length}: Line ${line}, Explanation: ${explanation.substring(0, 50)}...`);
        
        compileErrors.push({
          line,
          message: cleanMessage,
          code: codeSnippet.trim(),
          explanation: explanation,
          suggestion: suggestion,
          compilerMessage: compilerMessage,
          fix: specificFix,
          hasCorrectedCode: hasCorrectedCode,
        });
      });
    }

    // Transform runtime errors
    // IMPORTANT: Only show runtime errors if compilation was successful but execution failed
    // If compilation failed, there should be NO runtime errors (code never ran)
    if (backendData.runtime_errors && !backendData.runtime_errors.success && 
        backendData.compile_errors?.success !== false) {
      const errorMsg = backendData.runtime_errors.error || backendData.runtime_errors.stderr || "Runtime error occurred";
      
      // Get corrected code or fix instructions from LLM
      // BUT: Skip LLM setup instructions (don't show setup instructions as corrected code)
      let runtimeSuggestion = "Review the error message and fix the issue";
      let runtimeHasCorrectedCode = false;
      if (backendData.llm_explanation?.corrected_code) {
        const extractedCode = extractCorrectedCode(backendData.llm_explanation.corrected_code);
        if (extractedCode && extractedCode.trim().length > 0 && extractedCode.toLowerCase() !== 'null') {
          runtimeSuggestion = extractedCode;
          runtimeHasCorrectedCode = extractedCode.includes('#include') || 
                                    extractedCode.includes('public class') || 
                                    extractedCode.includes('class ') ||
                                    extractedCode.split('\n').length > 3 ||
                                    extractedCode.length > 100;
        }
      } else if (backendData.llm_explanation?.fix) {
        const fixText = backendData.llm_explanation.fix;
        // Check if fix is LLM setup instructions
        const isSetupInstructions = /GEMINI_API_KEY|check_api_key\.py|restart.*server|setup.*guide|api.*key|configuration/i.test(fixText);
        if (!isSetupInstructions) {
          // Check if fix contains code blocks
          if (fixText.includes('```')) {
            const codeMatch = fixText.match(/```(?:c|java|C|JAVA)?\n?(.*?)```/s);
            if (codeMatch && codeMatch[1].trim().length > 0) {
              runtimeSuggestion = codeMatch[1].trim();
              runtimeHasCorrectedCode = runtimeSuggestion.includes('#include') || 
                                        runtimeSuggestion.includes('public class') || 
                                        runtimeSuggestion.includes('class ') ||
                                        runtimeSuggestion.split('\n').length > 3;
            } else {
              runtimeSuggestion = fixText;
            }
          } else if (fixText.includes('#include') || fixText.includes('public class') || fixText.split('\n').length > 5) {
            runtimeSuggestion = fixText;
            runtimeHasCorrectedCode = true;
          } else {
            runtimeSuggestion = fixText;
          }
        }
      }
      
      // Get explanation - extract RUNTIME ERROR explanations only (those starting with "Runtime Error:" or "Runtime:")
      // IMPORTANT: Skip compile-time error explanations (those starting with "Line X:")
      let runtimeExplanation = "";
      const fullExplanation = backendData.llm_explanation?.cause || "";
      
      if (fullExplanation) {
        // Clean up explanation - remove JSON artifacts
        let cleanedExplanation = fullExplanation
          .replace(/```json\s*/gi, '')
          .replace(/```\s*/g, '')
          .replace(/^[\s\n]*\{[\s\n]*/g, '')
          .replace(/[\s\n]*\}[\s\n]*$/g, '')
          .replace(/^[\s\n]*\[[\s\n]*/g, '')
          .replace(/[\s\n]*\][\s\n]*$/g, '')
          .replace(/^\s*"cause"\s*:\s*/gi, '')
          .replace(/^\s*"summary"\s*:\s*/gi, '')
          .replace(/,\s*$/, '')
          .trim();
        
        // Split explanation into lines and find RUNTIME ERROR explanations only
        // Runtime errors start with "Runtime Error:" or "Runtime:"
        // Compile-time errors start with "Line X:" - ignore those here
        const lines = cleanedExplanation.split('\n');
        const runtimeExplanationLines: string[] = [];
        
        for (const expLine of lines) {
          const trimmed = expLine.trim();
          // Check if this is a runtime error explanation
          if (trimmed.match(/^(?:•|\d+\.|[-*])?\s*Runtime\s*Error?:/i) || 
              trimmed.match(/^Runtime\s*Error?:/i)) {
            // Extract the explanation part (remove "Runtime Error:" prefix)
            const explanationText = trimmed.replace(/^(?:•|\d+\.|[-*])?\s*Runtime\s*Error?:\s*/i, '')
                                           .replace(/^Runtime\s*Error?:\s*/i, '')
                                           .trim();
            if (explanationText) {
              runtimeExplanationLines.push(explanationText);
            }
          }
        }
        
        // Use the first runtime explanation found, or combine all if multiple
        if (runtimeExplanationLines.length > 0) {
          runtimeExplanation = runtimeExplanationLines.join(' ');
        }
      }
      
      // Fallback: if no runtime explanation found in cause, try summary or create generic one
      if (!runtimeExplanation || runtimeExplanation.trim().length < 10) {
        runtimeExplanation = backendData.llm_explanation?.summary || "";
        if (runtimeExplanation) {
          runtimeExplanation = runtimeExplanation.replace(/```json\s*/gi, '').replace(/```\s*/g, '');
          runtimeExplanation = runtimeExplanation.replace(/^[\s\n]*\{[\s\n]*/g, '').replace(/[\s\n]*\}[\s\n]*$/g, '');
          runtimeExplanation = runtimeExplanation.trim();
        }
      }
      
      // Final fallback: create a simple explanation
      if (!runtimeExplanation || runtimeExplanation.trim().length < 10) {
        runtimeExplanation = "A runtime error occurred during program execution. Please review the error message above.";
      }
      
      runtimeErrors.push({
        type: "Runtime Error",
        message: errorMsg,
        stackTrace: backendData.runtime_errors.stderr ? backendData.runtime_errors.stderr.split('\n').filter((l: string) => l.trim()) : [],
        explanation: runtimeExplanation,
        suggestion: runtimeSuggestion,
        hasCorrectedCode: runtimeHasCorrectedCode
      });
    }

    // Transform output analysis
    if (backendData.output_analysis) {
      if (backendData.output_analysis.match === false) {
        // Output mismatch - code doesn't run perfectly
        outputMismatch = {
          expected: backendData.output_analysis.expected || expectedOutput || "",
          actual: backendData.output_analysis.actual || backendData.runtime_errors?.stdout || "",
          explanation: backendData.llm_explanation?.cause || backendData.llm_explanation?.summary || "Output does not match expected result. There may be a logical error in the code.",
        };
      } else if (backendData.output_analysis.match === true) {
        // Output matches - code runs perfectly
        outputMismatch = null;
      } else {
        // No comparison made
        outputMismatch = null;
      }
    }

    // Check if we have corrected code for logical errors (output mismatch but no compile/runtime errors)
    let logicalErrorCorrectedCode = null;
    if (backendData.output_analysis && backendData.output_analysis.match === false && 
        compileErrors.length === 0 && runtimeErrors.length === 0 &&
        backendData.llm_explanation?.corrected_code) {
      logicalErrorCorrectedCode = extractCorrectedCode(backendData.llm_explanation.corrected_code);
    }
    
    // Extract full corrected code for compile errors (should fix all errors)
    let compileErrorCorrectedCode = null;
    if (compileErrors.length > 0) {
      // First, try to get from LLM explanation corrected_code
      if (backendData.llm_explanation?.corrected_code) {
        const extractedCode = extractCorrectedCode(backendData.llm_explanation.corrected_code);
        // Check if it looks like complete code (not just a snippet)
        // Be more lenient - accept if it has multiple lines or is reasonably long
        if (extractedCode && extractedCode.trim().length > 0 && extractedCode.toLowerCase() !== 'null' &&
            !extractedCode.includes('GEMINI_API_KEY') && 
            !extractedCode.includes('check_api_key.py') &&
            (extractedCode.includes('#include') || extractedCode.includes('public class') || 
             extractedCode.includes('int main') || extractedCode.includes('void main') ||
             extractedCode.split('\n').length > 3 || extractedCode.length > 50)) {
          compileErrorCorrectedCode = extractedCode;
        }
      }
      
      // If not found, check if any error has a complete corrected code in suggestion
      if (!compileErrorCorrectedCode) {
        for (const error of compileErrors) {
          if (error.suggestion && 
              !error.suggestion.includes('GEMINI_API_KEY') && 
              !error.suggestion.includes('check_api_key.py') &&
              !error.suggestion.includes('restart') &&
              (error.suggestion.includes('#include') || error.suggestion.includes('public class') || 
               error.suggestion.includes('int main') || error.suggestion.includes('void main') ||
               error.suggestion.split('\n').length > 3 || error.suggestion.length > 50)) {
            compileErrorCorrectedCode = error.suggestion;
            break; // Use the first complete corrected code found
          }
        }
      }
      
      // Final fallback: use first error's suggestion if it looks like complete code
      if (!compileErrorCorrectedCode && compileErrors[0]?.suggestion && 
          !compileErrors[0].suggestion.includes('GEMINI_API_KEY') &&
          !compileErrors[0].suggestion.includes('check_api_key.py') &&
          (compileErrors[0].suggestion.includes('#include') || compileErrors[0].suggestion.includes('public class') || 
           compileErrors[0].suggestion.includes('int main') || compileErrors[0].suggestion.includes('void main') ||
           compileErrors[0].suggestion.split('\n').length > 3 || compileErrors[0].suggestion.length > 50)) {
        compileErrorCorrectedCode = compileErrors[0].suggestion;
      }
    }
    
    // Debug: Log summary (remove in production)
    console.log('=== Error Processing Summary ===');
    console.log('Total compile errors:', compileErrors.length);
    console.log('Errors with explanations:', compileErrors.filter(e => e.explanation && e.explanation.trim().length > 10).length);
    console.log('Corrected code extracted:', !!compileErrorCorrectedCode);
    if (compileErrorCorrectedCode) {
      console.log('Corrected code preview:', compileErrorCorrectedCode.substring(0, 100) + '...');
      console.log('Corrected code length:', compileErrorCorrectedCode.length, 'lines:', compileErrorCorrectedCode.split('\n').length);
    }
    compileErrors.forEach((err, idx) => {
      console.log(`Error ${idx + 1}: Line ${err.line}, Message: ${err.message.substring(0, 50)}, Has explanation: ${!!err.explanation && err.explanation.length > 10}`);
    });
    
    return {
      compileErrors,
      runtimeErrors,
      outputMismatch,
      aiExplanations: backendData.llm_explanation ? [
        backendData.llm_explanation.summary,
        backendData.llm_explanation.cause,
        backendData.llm_explanation.fix,
      ].filter(Boolean) : [],
      executionSuccess: backendData.execution_success || false,
      programOutput: backendData.program_output || null,
      logicalErrorCorrectedCode: logicalErrorCorrectedCode,
      compileErrorCorrectedCode: compileErrorCorrectedCode,
      expectedOutput: expectedOutput || null,
      inputData: inputData || null,
      sectionRootCause: backendData.llm_explanation?.section_root_cause || undefined,
      cascadingErrors: backendData.llm_explanation?.cascading_errors || undefined,
    };
  };

  const handleAnalyze = async () => {
    if (!code.trim()) {
      toast.error("Please enter some code to analyze");
      return;
    }

    setIsAnalyzing(true);
    setResults(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language: language,
          code: code,
          input_data: inputData || undefined,
          expected_output: expectedOutput || undefined,
        }),
      }).catch((fetchError) => {
        // Network error - backend not running or CORS issue
        if (fetchError instanceof TypeError && fetchError.message.includes('fetch')) {
          throw new Error(`Cannot connect to backend server at ${API_BASE_URL}. Please make sure the backend is running on port 8000.`);
        }
        throw fetchError;
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const backendData = await response.json();
      const transformedResults = transformBackendResponse(backendData);
      setResults(transformedResults);
      
      // Check LLM status after analysis
      try {
        const llmResponse = await fetch(`${API_BASE_URL}/api/llm/status`);
        if (llmResponse.ok) {
          const status = await llmResponse.json();
          setLlmStatus(status);
        }
      } catch (error) {
        // Ignore LLM status check errors
      }
      
      // Show appropriate success message
      if (transformedResults.executionSuccess && transformedResults.compileErrors.length === 0 && transformedResults.runtimeErrors.length === 0) {
        toast.success("Code runs perfectly! ✓", {
          description: transformedResults.programOutput ? "Check output in results panel" : "No output generated"
        });
      } else {
        toast.success("Analysis complete!");
      }
    } catch (error) {
      console.error("Analysis error:", error);
      const errorMessage = error instanceof Error 
        ? error.message 
        : "Failed to analyze code. Please check the console for details.";
      
      toast.error(errorMessage, {
        duration: 5000,
        description: "Make sure the backend server is running: cd backend && python main.py"
      });
      setResults(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setCode(emptyCode[language]);
    setInputData('');
    setExpectedOutput('');
    setResults(null);
    toast.info("Workspace reset");
  };

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  const errorLines = results?.compileErrors.map((e) => e.line) || [];

  return (
    <section id="workspace" className="min-h-screen bg-background py-8 px-4 md:px-8">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-primary" />
              Code Workspace
            </h2>
            <p className="text-muted-foreground text-sm mt-1">
              Write or paste your code and let AI analyze it for errors
            </p>
          </div>

          <div className="flex items-center gap-3">
            <LanguageSelector
              selectedLanguage={language}
              onLanguageChange={handleLanguageChange}
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="rounded-lg"
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* LLM Status Banner */}
        {llmStatus && !llmStatus.available && (
          <div className="mb-6 p-4 rounded-lg border border-warning/30 bg-warning/10">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-foreground mb-1">LLM Service Not Available</h4>
                <p className="text-sm text-muted-foreground mb-3">{llmStatus.message}</p>
                {llmStatus.setup_guide && (
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p className="font-semibold text-foreground">Setup Guide:</p>
                    {Object.entries(llmStatus.setup_guide).map(([key, value]) => (
                      <p key={key} className="ml-4">• {value as string}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Main workspace grid */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left Panel - Code Input */}
          <div className="space-y-4">
            <div className="h-[500px]">
              <CodeEditor
                code={code}
                onChange={setCode}
                language={language}
                errorLines={errorLines}
              />
            </div>

            {/* Test case inputs */}
            <TestCaseInput
              inputData={inputData}
              expectedOutput={expectedOutput}
              onInputDataChange={setInputData}
              onExpectedOutputChange={setExpectedOutput}
            />

            {/* Action buttons */}
            <div className="flex gap-3">
              <Button
                variant="hero"
                size="lg"
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="flex-1"
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Analyze Code
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={handleReset}
                disabled={isAnalyzing}
              >
                <RotateCcw className="w-5 h-5" />
                Reset
              </Button>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="h-[700px] rounded-xl border border-border bg-card overflow-hidden">
            <ResultsPanel 
              results={results} 
              isLoading={isAnalyzing}
              onUpdateCode={(correctedCode) => {
                setCode(correctedCode);
                toast.success("Code updated with corrected version!");
              }}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Workspace;
