import { useState } from "react";
import { cn } from "@/lib/utils";
import { AlertTriangle, Bug, CheckCircle2, XCircle, Copy, Check, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface AnalysisResult {
  compileErrors: CompileError[];
  runtimeErrors: RuntimeError[];
  outputMismatch: OutputMismatch | null;
  aiExplanations: string[];
  executionSuccess?: boolean;
  programOutput?: string;
  sectionRootCause?: string;
  cascadingErrors?: string;
  logicalErrorCorrectedCode?: string | null;
  compileErrorCorrectedCode?: string | null;
  expectedOutput?: string;
  inputData?: string;
}

interface CompileError {
  line: number;
  message: string;
  code: string;
  explanation: string;
  suggestion: string;
  compilerMessage?: string;
  fix?: string;
  hasCorrectedCode?: boolean;
}

interface RuntimeError {
  type: string;
  message: string;
  stackTrace: string[];
  explanation: string;
  suggestion: string;
  hasCorrectedCode?: boolean;
}

interface OutputMismatch {
  expected: string;
  actual: string;
  explanation: string;
}

interface ResultsPanelProps {
  results: AnalysisResult | null;
  isLoading: boolean;
  onUpdateCode?: (code: string) => void;
}

// Helper function to extract result value (used by both component and OutputComparisonCard)
const extractResultValue = (output: string): string => {
  if (!output) return output;
  
  const trimmedOutput = output.trim();
  
  // Try to extract result from patterns like "Sum = 3", "Result = 5", etc.
  const resultPattern = /(?:Sum|Result|Output|Answer|Total)\s*=\s*(\d+)/i;
  const resultMatch = trimmedOutput.match(resultPattern);
  if (resultMatch) {
    return resultMatch[1];
  }
  
  // Try to find the last number in the output (often the result)
  const numbers = trimmedOutput.match(/\d+/g);
  if (numbers && numbers.length > 0) {
    // If there are multiple numbers, the last one is often the result
    // But if there's only one number, return it
    return numbers[numbers.length - 1];
  }
  
  // If it's just a number, return it
  if (/^\d+$/.test(trimmedOutput)) {
    return trimmedOutput;
  }
  
  // Fallback: return original output
  return trimmedOutput;
};

const ResultsPanel = ({ results, isLoading, onUpdateCode }: ResultsPanelProps) => {
  const [activeTab, setActiveTab] = useState<'compile' | 'runtime' | 'output'>('compile');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Function to format output with input prompts and values
  // Only formats when it matches specific input prompt patterns, otherwise returns output as-is
  const formatOutput = (output: string, inputData?: string, showFullFormat: boolean = true): string => {
    if (!output) return output;
    
    // Check if output contains "Enter" prompts - only format if it does
    const hasEnterPrompts = /Enter\s+[^:]+:/i.test(output);
    
    // If no "Enter" prompts, return output as-is (preserve all formatting and newlines)
    if (!hasEnterPrompts) {
      return output;
    }
    
    // Try to extract input prompts and values
    // Pattern: "Enter first number: Enter second number: Sum = 3"
    // Convert to: "Enter first number: value, Enter second number: value | Output -> Sum = 3"
    
    const trimmedOutput = output.trim();
    
    // Extract input values from inputData if available
    let inputValues: string[] = [];
    if (inputData) {
      // Split inputData by newlines or spaces to get individual values
      inputValues = inputData.trim().split(/[\s\n]+/).filter(v => v.length > 0);
    }
    
    // Pattern 1: "Enter first number: Enter second number: Sum = 3" (no values shown in output)
    const pattern1 = /Enter\s+first\s+number:\s*Enter\s+second\s+number:\s*Sum\s*=\s*(\d+)/i;
    const match1 = trimmedOutput.match(pattern1);
    if (match1) {
      // Try to use inputData values
      if (inputValues.length >= 2) {
        return `Enter first number: ${inputValues[0]}, Enter second number: ${inputValues[1]} | Output -> Sum = ${match1[1]}`;
      }
      // Try to extract values from output if they appear elsewhere
      const allNumbers = trimmedOutput.match(/\d+/g);
      if (allNumbers && allNumbers.length >= 3) {
        // Assume first two are inputs, last is result
        return `Enter first number: ${allNumbers[0]}, Enter second number: ${allNumbers[1]} | Output -> Sum = ${allNumbers[2]}`;
      }
      // Fallback: show result only
      return `Enter first number: [value], Enter second number: [value] | Output -> Sum = ${match1[1]}`;
    }
    
    // Pattern 2: "Enter first number: 1 Enter second number: 2 Sum = 3" (values in output)
    const pattern2 = /Enter\s+first\s+number:\s*(\d+)\s+Enter\s+second\s+number:\s*(\d+)\s+Sum\s*=\s*(\d+)/i;
    const match2 = trimmedOutput.match(pattern2);
    if (match2) {
      return `Enter first number: ${match2[1]}, Enter second number: ${match2[2]} | Output -> Sum = ${match2[3]}`;
    }
    
    // Pattern 3: Generic pattern - extract all "Enter X: value" pairs and result
    const enterPattern = /Enter\s+([^:]+):\s*(\d+)/gi;
    const enterMatches = Array.from(trimmedOutput.matchAll(enterPattern));
    
    if (enterMatches.length > 0) {
      const pairs: string[] = [];
      for (const match of enterMatches) {
        pairs.push(`Enter ${match[1].trim()}: ${match[2]}`);
      }
      
      // Try to find result (e.g., "Sum = 3", "Result = 5", etc.)
      const resultPattern = /([A-Za-z\s]+)=\s*(\d+)/i;
      const resultMatch = trimmedOutput.match(resultPattern);
      
      if (resultMatch) {
        return `${pairs.join(', ')} | Output -> ${resultMatch[1].trim()} = ${resultMatch[2]}`;
      } else if (pairs.length > 0) {
        // If we found input pairs but no result, just show the pairs
        return pairs.join(', ');
      }
    }
    
    // Pattern 4: Try to match prompts without values and use inputData
    const promptPattern = /Enter\s+first\s+number:\s*Enter\s+second\s+number:/i;
    if (promptPattern.test(trimmedOutput) && inputValues.length >= 2) {
      // Extract result number
      const resultMatch = trimmedOutput.match(/Sum\s*=\s*(\d+)/i);
      if (resultMatch) {
        return `Enter first number: ${inputValues[0]}, Enter second number: ${inputValues[1]} | Output -> Sum = ${resultMatch[1]}`;
      }
    }
    
    // If no specific pattern matches but has "Enter" prompts, return original output
    // This preserves multiline output with prompts
    return output;
  };

  if (isLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
          <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-primary animate-pulse" />
        </div>
        <p className="mt-6 text-lg font-medium text-foreground">Analyzing your code...</p>
        <p className="mt-2 text-sm text-muted-foreground">AI is examining for errors and issues</p>
        
        {/* Shimmer loading bars */}
        <div className="mt-8 w-full max-w-md space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-4 rounded-full bg-gradient-to-r from-secondary via-muted to-secondary bg-[length:200%_100%] animate-shimmer"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center">
        <div className="w-20 h-20 rounded-2xl bg-secondary flex items-center justify-center mb-6">
          <Bug className="w-10 h-10 text-muted-foreground" />
        </div>
        <h3 className="text-xl font-semibold text-foreground mb-2">Ready to Analyze</h3>
        <p className="text-muted-foreground max-w-sm">
          Write your code and click "Analyze Code" to detect compile-time, runtime, and logical errors
        </p>
      </div>
    );
  }

  const tabs = [
    {
      id: 'compile' as const,
      label: 'Compile Errors',
      icon: XCircle,
      count: results.compileErrors.length,
      color: 'destructive',
    },
    {
      id: 'runtime' as const,
      label: 'Runtime Errors',
      icon: AlertTriangle,
      count: results.runtimeErrors.length,
      color: 'warning',
    },
    {
      id: 'output' as const,
      label: 'Output Analysis',
      icon: results.outputMismatch ? AlertTriangle : CheckCircle2,
      count: results.outputMismatch ? 1 : 0,
      color: results.outputMismatch ? 'warning' : 'success',
    },
  ];

  // Check if code runs perfectly
  // Code runs perfectly if:
  // 1. Execution succeeded
  // 2. No compile errors
  // 3. No runtime errors
  // 4. Either no expected output provided OR output matches expected
  const codeRunsPerfectly = results.executionSuccess && 
                            results.compileErrors.length === 0 && 
                            results.runtimeErrors.length === 0 &&
                            (!results.outputMismatch); // No mismatch means either no expected output or it matches

  return (
    <div className="h-full flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-border bg-secondary/30 rounded-t-xl overflow-hidden">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-all",
              activeTab === tab.id
                ? "bg-card text-foreground border-b-2 border-primary"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
            )}
          >
            <tab.icon className={cn(
              "w-4 h-4",
              tab.color === 'destructive' && "text-destructive",
              tab.color === 'warning' && "text-warning",
              tab.color === 'success' && "text-success"
            )} />
            {tab.label}
            {tab.count > 0 && (
              <span className={cn(
                "px-2 py-0.5 rounded-full text-xs font-semibold",
                tab.color === 'destructive' && "bg-destructive/20 text-destructive",
                tab.color === 'warning' && "bg-warning/20 text-warning",
                tab.color === 'success' && "bg-success/20 text-success"
              )}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Show success banner if code runs perfectly */}
        {codeRunsPerfectly && (
          <div className="rounded-xl border-2 border-success/50 bg-success/10 p-6 mb-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-success/20 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 className="w-7 h-7 text-success" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-foreground mb-2">✓ Code Runs Perfectly!</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Your code compiled successfully and executed without any errors.
                </p>
                {results.programOutput && (
                  <div className="mt-4">
                    <p className="text-sm font-semibold text-foreground mb-2">Program Output:</p>
                    <pre className="font-mono text-sm bg-card p-4 rounded-lg border border-border text-foreground whitespace-pre-wrap overflow-x-auto">
                      {formatOutput(results.programOutput, results.inputData) || "(No output)"}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'compile' && (
          <>
            {results.compileErrors.length === 0 ? (
              <SuccessCard message="No compile-time errors found!" />
            ) : (
              <>
                {/* Summary section: Show all error explanations point-wise */}
                <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 mb-4">
                  <div className="flex items-start gap-3 mb-4">
                    <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="font-semibold text-foreground mb-1">Compile Errors Detected</h3>
                    </div>
                  </div>
                  
                  {/* Error Explanations */}
                  <div className="space-y-6 pl-8">
                    {results.compileErrors && results.compileErrors.length > 0 ? (
                      results.compileErrors.map((error, i) => {
                        let explanation = error.explanation || error.message || `Error at line ${error.line}`;
                        explanation = explanation
                          .replace(/^(?:What is the error|Error|Issue|Problem)[:\s]+/i, '')
                          .replace(/^(?:How to resolve|Resolution|Fix|Solution|How to fix|How to correct)[:\s]+/i, '')
                          .trim();
                        
                        return (
                          <div key={`error-${i}-${error.line}`} className="flex flex-col gap-1 text-sm text-foreground">
                            <h4 className="font-semibold text-destructive text-base">Error {i + 1}</h4>
                            <p><strong>Line:</strong> {error.line}</p>
                            <p><strong>Compiler Message:</strong> {error.compilerMessage || error.message}</p>
                            {explanation && explanation.length > 5 && (
                              <p><strong>Explanation:</strong> <span className="whitespace-pre-wrap">{explanation}</span></p>
                            )}
                            {(error.fix || error.suggestion) && (
                              <p><strong>Fix:</strong> <code className="bg-muted px-1.5 py-0.5 rounded text-[13px]">{error.fix || error.suggestion}</code></p>
                            )}
                          </div>
                        );
                      })
                    ) : (
                      <p className="text-sm text-muted-foreground">No error explanations available</p>
                    )}
                  </div>

                  {results.sectionRootCause && (
                    <div className="mt-8 pt-4 border-t border-destructive/20 pl-8">
                      <h4 className="font-semibold text-warning text-base mb-2">SECTION: Root Cause</h4>
                      <p className="text-sm text-foreground whitespace-pre-wrap">{results.sectionRootCause}</p>
                    </div>
                  )}
                </div>

                {/* Individual Error Cards - Show code snippets for each error - Show ALL errors */}
                {results.compileErrors && results.compileErrors.length > 0 ? (
                  results.compileErrors.map((error, i) => (
                    <div key={`card-${i}-${error.line}`} className="rounded-xl border border-destructive/30 overflow-hidden mb-4">
                      {/* Header - Error Message */}
                      <div className="flex items-start gap-3 p-4 bg-destructive/10">
                        <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <h4 className="font-semibold text-foreground mb-1">{`Line ${error.line}: ${error.message}`}</h4>
                          <p className="text-xs text-muted-foreground">
                            Error Location: Line {error.line}
                          </p>
                        </div>
                      </div>

                      {/* Error Code Snippet */}
                      {error.code && (
                        <div className="px-4 py-3 bg-code-bg border-y border-border">
                          <div className="flex items-center gap-2 mb-2">
                            <p className="text-xs font-semibold text-muted-foreground">
                              Code at line {error.line}:
                            </p>
                          </div>
                          <pre className="font-mono text-sm text-foreground overflow-x-auto">{error.code}</pre>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No error details available</p>
                )}

                {/* Show Full Corrected Code if available - Show once at the bottom */}
                {results.compileErrors.length > 0 && results.compileErrorCorrectedCode && (
                  <div className="mt-4 rounded-xl border-2 border-success/50 bg-success/5 p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-success" />
                        <h4 className="font-semibold text-success text-base">SECTION: Corrected Code</h4>
                      </div>
                      <div className="flex gap-2">
                        {onUpdateCode && (
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => onUpdateCode(results.compileErrorCorrectedCode!)}
                            className="h-7 text-xs bg-primary hover:bg-primary/90"
                          >
                            Update Code
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopy(results.compileErrorCorrectedCode!, results.compileErrors.length)}
                          className="h-7 text-xs"
                        >
                          {copiedIndex === results.compileErrors.length ? (
                            <Check className="w-3 h-3 mr-1" />
                          ) : (
                            <Copy className="w-3 h-3 mr-1" />
                          )}
                          {copiedIndex === results.compileErrors.length ? 'Copied!' : 'Copy'}
                        </Button>
                      </div>
                    </div>
                    <pre className="font-mono text-sm text-foreground whitespace-pre-wrap overflow-x-auto bg-card p-4 rounded-lg border border-border max-h-96 overflow-y-auto">
                      {results.compileErrorCorrectedCode}
                    </pre>
                  </div>
                )}
              </>
            )}
          </>
        )}

        {activeTab === 'runtime' && (
          <>
            {results.runtimeErrors.length === 0 ? (
              <SuccessCard message="No runtime errors detected!" />
            ) : (
              results.runtimeErrors.map((error, i) => (
                <ErrorCard
                  key={i}
                  type="runtime"
                  title={`${error.type}: ${error.message}`}
                  stackTrace={error.stackTrace}
                  explanation={error.explanation}
                  suggestion={error.suggestion}
                  onCopy={() => handleCopy(error.suggestion, i + 100)}
                  isCopied={copiedIndex === i + 100}
                  onUpdateCode={onUpdateCode && error.suggestion && (error.suggestion.includes('#include') || error.suggestion.includes('public class')) 
                    ? () => onUpdateCode(error.suggestion) 
                    : undefined}
                  hasCorrectedCode={error.hasCorrectedCode || (error.suggestion && (error.suggestion.includes('#include') || error.suggestion.includes('public class') || error.suggestion.length > 100))}
                />
              ))
            )}
          </>
        )}

        {activeTab === 'output' && (
          <>
            {!results.outputMismatch ? (
              <>
                {codeRunsPerfectly && results.programOutput ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 p-6 rounded-xl border-2 border-success/50 bg-success/10">
                      <div className="w-12 h-12 rounded-xl bg-success/20 flex items-center justify-center flex-shrink-0">
                        <CheckCircle2 className="w-7 h-7 text-success" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-foreground mb-2">✓ Code Runs Perfectly!</h3>
                        <p className="text-sm text-muted-foreground mb-4">
                          The actual output matches the expected output. Your code is working correctly!
                        </p>
                        <div className="mt-4 space-y-3">
                          <div>
                            <p className="text-sm font-semibold text-foreground mb-2">Actual Output:</p>
                            <pre className="font-mono text-sm bg-card p-3 rounded-lg border border-border text-foreground whitespace-pre-wrap overflow-x-auto">
                              {results.expectedOutput 
                                ? extractResultValue(results.programOutput.trim())
                                : formatOutput(results.programOutput.trim(), results.inputData, true)}
                            </pre>
                          </div>
                          {results.expectedOutput && (
                            <div>
                              <p className="text-sm font-semibold text-foreground mb-2">Expected Output:</p>
                              <pre className="font-mono text-sm bg-success/5 p-3 rounded-lg border border-success/20 text-foreground whitespace-pre-wrap overflow-x-auto">
                                {results.expectedOutput.trim()}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <SuccessCard message="Output matches expected result!" />
                )}
              </>
            ) : (
              <>
                <OutputComparisonCard
                  expected={results.outputMismatch.expected}
                  actual={results.outputMismatch.actual}
                  explanation={results.outputMismatch.explanation}
                />
                {/* Show corrected code if available for logical errors */}
                {results.logicalErrorCorrectedCode && (
                  <div className="mt-4 p-4 rounded-xl border border-warning/30 bg-warning/5">
                    <div className="flex items-start gap-2 mb-3">
                      <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-warning mb-1">Logical Error Detected</p>
                        <p className="text-sm text-muted-foreground">
                          The code compiles and runs, but produces incorrect output. This indicates a logical error in your code logic or calculations.
                        </p>
                      </div>
                    </div>
                    <div className="mt-3">
                      <p className="text-xs font-semibold text-success mb-2">Corrected Code:</p>
                      <pre className="font-mono text-xs bg-card p-3 rounded-lg border border-border text-foreground whitespace-pre-wrap overflow-x-auto max-h-60 overflow-y-auto">
                        {results.logicalErrorCorrectedCode}
                      </pre>
                      {onUpdateCode && (
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => onUpdateCode(results.logicalErrorCorrectedCode!)}
                          className="mt-3 bg-primary hover:bg-primary/90"
                        >
                          Update Code
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};

const SuccessCard = ({ message }: { message: string }) => (
  <div className="flex items-center gap-4 p-6 rounded-xl border border-success/30 bg-success/5">
    <div className="w-12 h-12 rounded-xl bg-success/20 flex items-center justify-center">
      <CheckCircle2 className="w-6 h-6 text-success" />
    </div>
    <div>
      <h4 className="font-semibold text-foreground">{message}</h4>
      <p className="text-sm text-muted-foreground">Your code passed this check</p>
    </div>
  </div>
);

interface ErrorCardProps {
  type: 'compile' | 'runtime';
  title: string;
  code?: string;
  stackTrace?: string[];
  explanation: string;
  suggestion: string;
  onCopy: () => void;
  isCopied: boolean;
  onUpdateCode?: () => void;
  hasCorrectedCode?: boolean;
  showSimplifiedExplanation?: boolean; // If true, show simple explanation without "What/How" structure
}

const ErrorCard = ({ type, title, code, stackTrace, explanation, suggestion, onCopy, isCopied, onUpdateCode, hasCorrectedCode, showSimplifiedExplanation = false }: ErrorCardProps) => {
  // Format explanation to display point-wise and clean JSON artifacts
  const formatExplanation = (exp: string, simplified: boolean = false): string => {
    if (!exp) return "";
    
    // Remove JSON artifacts first
    let cleaned = exp
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
    
    // If simplified mode, remove "What is the error:" and "How to resolve:" sections
    if (simplified) {
      cleaned = cleaned
        .replace(/^(?:What is the error|Error|Issue|Problem)[:\s]+/gi, '')
        .replace(/^(?:How to resolve|Resolution|Fix|Solution|How to fix|How to correct)[:\s]+/gi, '')
        .replace(/\n\n(?:What is the error|Error|Issue|Problem)[:\s]+/gi, '\n\n')
        .replace(/\n\n(?:How to resolve|Resolution|Fix|Solution|How to fix|How to correct)[:\s]+/gi, '\n\n')
        .trim();
    }
    
    // If it's already in point-wise format (has bullets or numbers), return as-is
    if (cleaned.includes('•') || cleaned.includes('-') || /^\d+\./.test(cleaned.trim())) {
      return cleaned;
    }
    
    // If it contains line numbers, try to format it better
    // Split by common separators and format as points
    const lines = cleaned.split(/\n+/).filter(line => line.trim());
    if (lines.length > 1) {
      return lines.map(line => {
        const trimmed = line.trim();
        // Skip empty lines and JSON artifacts
        if (!trimmed || trimmed === ',' || trimmed === ']' || trimmed === '}' || trimmed === '[' || trimmed === '{') {
          return '';
        }
        // If line starts with a number or bullet, keep it
        if (/^[\d•\-\*]/.test(trimmed)) {
          return trimmed;
        }
        // Otherwise, add bullet
        return `• ${trimmed}`;
      }).filter(line => line.length > 0).join('\n');
    }
    
    // Single line - return as-is
    return cleaned;
  };

  const formattedExplanation = formatExplanation(explanation, showSimplifiedExplanation);

  return (
    <div className={cn(
      "rounded-xl border overflow-hidden transition-all hover:shadow-lg",
      type === 'compile' ? "border-destructive/30 error-glow" : "border-warning/30 warning-glow"
    )}>
      {/* Header - Error Message with Line Number */}
      <div className={cn(
        "flex items-start gap-3 p-4",
        type === 'compile' ? "bg-destructive/10" : "bg-warning/10"
      )}>
        {type === 'compile' ? (
          <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
        )}
        <div className="flex-1">
          <h4 className="font-semibold text-foreground mb-1">{title}</h4>
          {/* Extract and display line number prominently for compile errors */}
          {type === 'compile' && code && (
            <p className="text-xs text-muted-foreground">
              Error Location: {title.match(/Line\s+(\d+)/)?.[1] || 'Unknown line'}
            </p>
          )}
        </div>
      </div>

      {/* Error Code Snippet with Line Number */}
      {code && (
        <div className="px-4 py-3 bg-code-bg border-y border-border">
          <div className="flex items-center gap-2 mb-2">
            <p className="text-xs font-semibold text-muted-foreground">
              {type === 'compile' ? `Code at ${title.match(/Line\s+(\d+)/)?.[1] || 'error'} line:` : 'Error Code:'}
            </p>
          </div>
          <pre className="font-mono text-sm text-foreground overflow-x-auto">{code}</pre>
        </div>
      )}

      {/* Stack trace (for runtime errors) */}
      {stackTrace && stackTrace.length > 0 && (
        <div className="px-4 py-3 bg-code-bg border-y border-border">
          <p className="text-xs font-semibold text-muted-foreground mb-2">Stack Trace:</p>
          {stackTrace.map((line, i) => (
            <p key={i} className="font-mono text-xs text-muted-foreground">{line}</p>
          ))}
        </div>
      )}

      {/* Content Section */}
      <div className="p-4 space-y-4 bg-card">
        {/* Simplified Explanation - Only show if not simplified mode (for runtime errors) */}
        {formattedExplanation && !showSimplifiedExplanation && (
          <div className="flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-primary flex-shrink-0 mt-1" />
            <div className="flex-1">
              <p className="text-xs font-semibold text-primary mb-1">Explanation</p>
              <div className="text-sm text-foreground whitespace-pre-wrap">
                {formattedExplanation.split('\n').map((line, idx) => (
                  <p key={idx} className={idx > 0 ? 'mt-1' : ''}>{line || '\u00A0'}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Corrected Code / Suggested Fix */}
        {/* Don't show if suggestion is LLM setup instructions */}
        {suggestion && suggestion.trim().length > 0 && 
         !/GEMINI_API_KEY|check_api_key\.py|restart.*server|setup.*guide|api.*key.*configuration|verify.*gemini/i.test(suggestion) && (
          <div className="p-3 rounded-lg bg-success/5 border border-success/20">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold text-success">
                {hasCorrectedCode || suggestion.includes('#include') || suggestion.includes('public class') || suggestion.split('\n').length > 2 ? 'Corrected Code' : 'Suggested Fix'}
              </p>
              <div className="flex gap-2">
                {(hasCorrectedCode || suggestion.includes('#include') || suggestion.includes('public class') || suggestion.split('\n').length > 2) && onUpdateCode && (
                  <Button
                    variant="default"
                    size="sm"
                    onClick={onUpdateCode}
                    className="h-7 text-xs bg-primary hover:bg-primary/90"
                  >
                    Update Code
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onCopy}
                  className="h-7 text-xs"
                >
                  {isCopied ? (
                    <Check className="w-3 h-3 mr-1" />
                  ) : (
                    <Copy className="w-3 h-3 mr-1" />
                  )}
                  {isCopied ? 'Copied!' : 'Copy'}
                </Button>
              </div>
            </div>
            <pre className="font-mono text-sm text-foreground whitespace-pre-wrap overflow-x-auto mt-2">{suggestion}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

interface OutputComparisonCardProps {
  expected: string;
  actual: string;
  explanation: string;
}

const OutputComparisonCard = ({ expected, actual, explanation }: OutputComparisonCardProps) => {
  // Extract result value from actual output
  const actualResult = extractResultValue(actual);
  
  return (
    <div className="rounded-xl border border-warning/30 overflow-hidden warning-glow">
      <div className="flex items-center gap-3 p-4 bg-warning/10">
        <AlertTriangle className="w-5 h-5 text-warning" />
        <div className="flex-1">
          <h4 className="font-semibold text-foreground">✗ Output Mismatch</h4>
          <p className="text-xs text-muted-foreground mt-1">Actual output does not match expected output - Logical error detected</p>
        </div>
      </div>

      <div className="grid grid-cols-2 divide-x divide-border">
        <div className="p-4">
          <p className="text-xs font-semibold text-success mb-2 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Expected Output
          </p>
          <pre className="font-mono text-sm bg-success/5 p-3 rounded-lg border border-success/20 text-foreground whitespace-pre-wrap">
            {expected.trim()}
          </pre>
        </div>
        <div className="p-4">
          <p className="text-xs font-semibold text-destructive mb-2 flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            Actual Output
          </p>
          <pre className="font-mono text-sm bg-destructive/5 p-3 rounded-lg border border-destructive/20 text-foreground whitespace-pre-wrap">
            {actualResult}
          </pre>
        </div>
      </div>

      <div className="p-4 bg-card border-t border-border">
        <div className="flex items-start gap-2">
          <Sparkles className="w-4 h-4 text-primary flex-shrink-0 mt-1" />
          <div>
            <p className="text-xs font-semibold text-primary mb-1">AI Explanation</p>
            <p className="text-sm text-foreground">{explanation}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;
