import { useState, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  language: 'C' | 'Java';
  errorLines?: number[];
}

const CodeEditor = ({ code, onChange, language, errorLines = [] }: CodeEditorProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  const isPastingRef = useRef(false);
  const [lineCount, setLineCount] = useState(1);

  useEffect(() => {
    const lines = code.split('\n').length;
    setLineCount(Math.max(lines, 20));
  }, [code]);

  // Sync scroll between textarea, line numbers, and overlay
  const handleScroll = () => {
    if (textareaRef.current && lineNumbersRef.current && overlayRef.current) {
      const scrollTop = textareaRef.current.scrollTop;
      lineNumbersRef.current.scrollTop = scrollTop;
      overlayRef.current.scrollTop = scrollTop;
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget;
    const newValue = textarea.value;
    
    // Don't interfere with paste operations - let browser handle selection naturally
    onChange(newValue);
    
    // Sync scroll after change
    requestAnimationFrame(() => {
      handleScroll();
    });
  };

  // Handle paste events to detect when user is pasting
  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    isPastingRef.current = true;
    // Let the browser handle the paste naturally
    setTimeout(() => {
      isPastingRef.current = false;
      // Sync scroll after paste
      requestAnimationFrame(() => {
        handleScroll();
      });
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue = code.substring(0, start) + '    ' + code.substring(end);
      
      onChange(newValue);
      
      // Restore cursor position after tab insertion
      requestAnimationFrame(() => {
        if (textareaRef.current) {
          const newPos = start + 4;
          textareaRef.current.setSelectionRange(newPos, newPos);
        }
      });
    } else if (e.key === 'Delete' || e.key === 'Backspace') {
      // Allow normal deletion - don't interfere
      // The browser will handle it naturally
    }
  };

  return (
    <div className="relative h-full rounded-xl overflow-hidden border border-border bg-code-bg">
      {/* Editor header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-secondary/50">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-destructive/60" />
            <div className="w-3 h-3 rounded-full bg-warning/60" />
            <div className="w-3 h-3 rounded-full bg-success/60" />
          </div>
          <span className="text-xs font-mono text-muted-foreground ml-3">
            main.{language === 'C' ? 'c' : 'java'}
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          {language} Code Editor
        </span>
      </div>

      {/* Editor body */}
      <div className="flex h-[calc(100%-40px)] overflow-hidden">
        {/* Line numbers */}
        <div
          ref={lineNumbersRef}
          className="flex-shrink-0 py-4 px-3 text-right select-none overflow-y-auto overflow-x-hidden bg-secondary/30 scrollbar-thin"
          style={{ 
            scrollbarWidth: 'thin',
            msOverflowStyle: 'none'
          }}
        >
          {Array.from({ length: lineCount }, (_, i) => (
            <div
              key={i + 1}
              className={cn(
                "font-mono text-xs leading-6 text-line-number transition-colors",
                errorLines.includes(i + 1) && "text-destructive font-semibold"
              )}
            >
              {i + 1}
            </div>
          ))}
        </div>

        {/* Code area */}
        <div className="relative flex-1 overflow-hidden">
          {/* Syntax highlighted overlay - must match textarea styling exactly */}
          <div 
            ref={overlayRef}
            className="absolute inset-0 py-4 px-4 pointer-events-none overflow-y-scroll overflow-x-hidden hide-scrollbar select-none"
            style={{ 
              zIndex: 0,
              userSelect: 'none',
              WebkitUserSelect: 'none',
              MozUserSelect: 'none',
              msUserSelect: 'none'
            }}
          >
            {code.split('\n').map((line, i) => (
              <div
                key={i}
                className={cn(
                  "font-mono text-sm leading-6 whitespace-pre",
                  errorLines.includes(i + 1) && "bg-destructive/10 -mx-4 px-4 border-l-2 border-destructive"
                )}
              >
                <SyntaxHighlight code={line} language={language} />
                {line === '' && '\u00A0'}
              </div>
            ))}
          </div>

          {/* Actual textarea - must be perfectly aligned with overlay */}
          <textarea
            ref={textareaRef}
            value={code}
            onChange={handleChange}
            onPaste={handlePaste}
            onScroll={handleScroll}
            onKeyDown={handleKeyDown}
            onMouseDown={(e) => {
              // Ensure textarea gets focus and selection works
              e.currentTarget.focus();
            }}
            onMouseUp={(e) => {
              // Ensure selection is preserved
              e.currentTarget.focus();
            }}
            className="absolute inset-0 w-full h-full py-4 px-4 font-mono text-sm leading-6 bg-transparent text-transparent resize-none focus:outline-none cursor-text overflow-y-auto overflow-x-hidden"
            style={{ 
              caretColor: 'hsl(var(--foreground))',
              WebkitTextFillColor: 'transparent',
              zIndex: 1,
              color: 'transparent',
              cursor: 'text',
              userSelect: 'text',
              WebkitUserSelect: 'text',
              MozUserSelect: 'text',
              msUserSelect: 'text',
              pointerEvents: 'auto'
            }}
            spellCheck={false}
            placeholder={`// Write your ${language} code here...`}
          />
        </div>
      </div>
    </div>
  );
};

// Simple syntax highlighting component
const SyntaxHighlight = ({ code, language }: { code: string; language: 'C' | 'Java' }) => {
  const keywords = language === 'C'
    ? ['int', 'char', 'float', 'double', 'void', 'if', 'else', 'for', 'while', 'return', 'include', 'define', 'struct', 'typedef', 'printf', 'scanf', 'main']
    : ['public', 'private', 'protected', 'class', 'interface', 'extends', 'implements', 'static', 'void', 'int', 'String', 'boolean', 'if', 'else', 'for', 'while', 'return', 'new', 'import', 'package', 'System'];

  const highlightCode = (text: string) => {
    // Comments
    if (text.includes('//')) {
      const [before, after] = text.split('//');
      return (
        <>
          {highlightCode(before)}
          <span className="text-muted-foreground/60">//{after}</span>
        </>
      );
    }

    // Simple tokenization
    const tokens = text.split(/(\s+|[(){}[\];,.<>])/);
    
    return tokens.map((token, i) => {
      if (keywords.includes(token)) {
        return <span key={i} className="text-primary font-medium">{token}</span>;
      }
      if (/^".*"$/.test(token) || /^'.*'$/.test(token)) {
        return <span key={i} className="text-success">{token}</span>;
      }
      if (/^\d+$/.test(token)) {
        return <span key={i} className="text-warning">{token}</span>;
      }
      if (token.startsWith('#')) {
        return <span key={i} className="text-accent">{token}</span>;
      }
      return <span key={i} className="text-foreground">{token}</span>;
    });
  };

  return <>{highlightCode(code)}</>;
};

export default CodeEditor;
