# Complete Technology Stack Documentation

## Project Overview
AI-powered compiler debugging assistant that analyzes C and Java programs, provides error explanations, and suggests fixes using Google Gemini AI.

---

## Frontend Technologies

### Core Framework & Language
- **React** 18.3.1 - UI framework
- **TypeScript** 5.8.3 - Type-safe JavaScript
- **Vite** 5.4.19 - Build tool and dev server (with React SWC plugin for faster compilation)

### Routing & Navigation
- **React Router DOM** 6.30.1 - Client-side routing

### UI Component Libraries
- **shadcn/ui** - Component library built on Radix UI primitives
- **Radix UI** - Headless UI component primitives:
  - `@radix-ui/react-accordion` 1.2.11
  - `@radix-ui/react-alert-dialog` 1.1.14
  - `@radix-ui/react-aspect-ratio` 1.1.7
  - `@radix-ui/react-avatar` 1.1.10
  - `@radix-ui/react-checkbox` 1.3.2
  - `@radix-ui/react-collapsible` 1.1.11
  - `@radix-ui/react-context-menu` 2.2.15
  - `@radix-ui/react-dialog` 1.1.14
  - `@radix-ui/react-dropdown-menu` 2.1.15
  - `@radix-ui/react-hover-card` 1.1.14
  - `@radix-ui/react-label` 2.1.7
  - `@radix-ui/react-menubar` 1.1.15
  - `@radix-ui/react-navigation-menu` 1.2.13
  - `@radix-ui/react-popover` 1.1.14
  - `@radix-ui/react-progress` 1.1.7
  - `@radix-ui/react-radio-group` 1.3.7
  - `@radix-ui/react-scroll-area` 1.2.9
  - `@radix-ui/react-select` 2.2.5
  - `@radix-ui/react-separator` 1.1.7
  - `@radix-ui/react-slider` 1.3.5
  - `@radix-ui/react-slot` 1.2.3
  - `@radix-ui/react-switch` 1.2.5
  - `@radix-ui/react-tabs` 1.1.12
  - `@radix-ui/react-toast` 1.2.14
  - `@radix-ui/react-toggle` 1.1.9
  - `@radix-ui/react-toggle-group` 1.1.10
  - `@radix-ui/react-tooltip` 1.2.7

### Styling & CSS
- **Tailwind CSS** 3.4.17 - Utility-first CSS framework
- **Tailwind CSS Animate** 1.0.7 - Animation utilities
- **PostCSS** 8.5.6 - CSS processing
- **Autoprefixer** 10.4.21 - CSS vendor prefixing
- **@tailwindcss/typography** 0.5.16 - Typography plugin

### Form Handling & Validation
- **React Hook Form** 7.61.1 - Form state management
- **Zod** 3.25.76 - Schema validation
- **@hookform/resolvers** 3.10.0 - Form validation resolvers (supports Zod, Yup, Vest, etc.)

### State Management & Data Fetching
- **TanStack React Query** 5.83.0 (formerly React Query) - Server state management and data fetching

### UI Utilities & Helpers
- **clsx** 2.1.1 - Conditional className utility
- **tailwind-merge** 2.6.0 - Merge Tailwind classes
- **class-variance-authority** 0.7.1 - Component variant management

### Icons & Graphics
- **Lucide React** 0.462.0 - Icon library

### Data Visualization
- **Recharts** 2.15.4 - React charting library

### Notifications & Toasts
- **Sonner** 1.7.4 - Toast notification library

### Additional UI Components
- **cmdk** 1.1.1 - Command menu component
- **date-fns** 3.6.0 - Date utility library
- **embla-carousel-react** 8.6.0 - Carousel component
- **input-otp** 1.4.2 - OTP input component
- **react-day-picker** 8.10.1 - Date picker
- **react-resizable-panels** 2.1.9 - Resizable panel layouts
- **next-themes** 0.3.0 - Theme switching
- **vaul** 0.9.9 - Drawer component

### Development Tools
- **ESLint** 9.32.0 - Code linting
- **TypeScript ESLint** 8.38.0 - TypeScript-specific linting
- **Lovable Tagger** 1.1.13 - Development tool (component tagging)

### Build & Development
- **@vitejs/plugin-react-swc** 3.11.0 - React plugin for Vite (uses SWC for faster compilation)
- **@types/node** 22.16.5 - Node.js TypeScript definitions
- **@types/react** 18.3.23 - React TypeScript definitions
- **@types/react-dom** 18.3.7 - React DOM TypeScript definitions

---

## Backend Technologies

### Core Framework & Runtime
- **Python** - Programming language
- **FastAPI** 0.115.0+ - Modern, fast web framework for building APIs
- **Uvicorn** 0.32.0+ (standard) - ASGI web server implementation

### Data Validation & Serialization
- **Pydantic** 2.9.0+ - Data validation using Python type annotations

### Environment Management
- **python-dotenv** 1.0.1+ - Load environment variables from .env file

### AI/LLM Integration
- **google-genai** 0.2.0+ - Google Gemini AI SDK (new API)
- **google-generativeai** 0.8.3 - Google Gemini AI SDK (fallback/legacy API)

### HTTP & Multipart Handling
- **python-multipart** 0.9+ - Support for form data parsing
- **requests** 2.32.3+ - HTTP library (for API calls if needed)

### System Integration
- **subprocess** (Python standard library) - Execute system commands (GCC, Javac, Java)
- **tempfile** (Python standard library) - Temporary file management
- **os** (Python standard library) - Operating system interface
- **platform** (Python standard library) - Platform identification
- **shutil** (Python standard library) - File operations
- **re** (Python standard library) - Regular expressions
- **json** (Python standard library) - JSON parsing
- **logging** (Python standard library) - Logging framework

### Compilers & Runtime (External Dependencies)
- **GCC (GNU Compiler Collection)** - C compiler (must be installed on system)
- **JDK (Java Development Kit)** - Java compiler (javac) and runtime (java) (must be installed on system)

---

## APIs Used

### External APIs
1. **Google Gemini API**
   - Models used:
     - `gemini-2.5-flash` (primary, new API)
     - `gemini-pro` (fallback, legacy API)
   - Purpose: Generate human-readable error explanations and code fixes
   - Endpoints: Google AI Studio API
   - Authentication: API key via environment variable (GEMINI_API_KEY)

### Backend API Endpoints
1. **POST /api/analyze**
   - Main analysis endpoint
   - Accepts: Code, language, optional input/output
   - Returns: Compilation errors, runtime errors, LLM explanations, corrected code

2. **GET /api/llm/status**
   - Check LLM service availability
   - Returns: Service status, configuration guidance

3. **GET /**
   - Health check endpoint
   - Returns: Service status

4. **GET /health**
   - Detailed health check
   - Returns: Compiler availability, LLM status

---

## Algorithms & Techniques

### Code Compilation
1. **C Compilation Algorithm**
   - Uses GCC compiler with flags: `-Wall -std=c11`
   - Error parsing with regex patterns to extract line numbers
   - Error format: `file.c:line:column: error: message`

2. **Java Compilation Algorithm**
   - Uses Javac compiler with flags: `-encoding UTF-8 -Xlint:all`
   - Class name extraction using regex: `public class (\w+)`
   - Error parsing: `File.java:line: error: message`

### Error Parsing Algorithms
1. **Regex Pattern Matching**
   - Extract line numbers from compiler error messages
   - Pattern: `:(\d+)(?::\d+)?:\s*(?:fatal\s+)?error:`
   - Alternative patterns for different error formats

2. **Error Classification**
   - Syntax errors
   - Type mismatches
   - Missing symbols
   - Compilation warnings

### Code Execution
1. **Process Execution**
   - Uses Python `subprocess` module
   - Timeout management (10 seconds for execution)
   - Input/output redirection (stdin/stdout/stderr)
   - Platform-specific handling (Windows .exe extension)

2. **Security Measures**
   - Execution timeout prevents infinite loops
   - Output size limits (10MB max)
   - Temporary file cleanup
   - Isolated execution environment

### Output Comparison Algorithms
1. **Exact Match Comparison**
   - Normalized whitespace comparison
   - Line ending normalization (CRLF, LF, CR)

2. **Line-by-Line Comparison**
   - Compare outputs line by line
   - Strip trailing whitespace per line

3. **Smart Matching**
   - Contains matching (check if expected output appears in actual)
   - Word boundary matching for non-numeric values
   - Pattern: `\b(expected)\b`

4. **Numeric Matching**
   - Extract numbers using regex: `-?\d+\.?\d*`
   - Compare numeric values even if formatted differently
   - Handles cases like "Sum = 3" vs "3"

5. **Difference Detection**
   - Line-by-line diff generation
   - Maximum 10 differences tracked
   - Numeric difference calculation

### Programmatic Code Fixing (Java-specific)
1. **Pattern-Based Fixes**
   - Missing brackets: `String args` → `String[] args`
   - Missing semicolons: Line ending detection and addition
   - Type mismatches: String to numeric conversion
   - Missing parentheses: Balance checking and addition
   - Missing braces: Loop structure detection

2. **Regex-Based Transformations**
   - Pattern matching for common error patterns
   - Context-aware replacements
   - Undefined variable replacement (e.g., "zero" → "0")

3. **Code Normalization**
   - Remove blank lines for comparison
   - Whitespace normalization
   - Character-by-character comparison validation

### LLM Integration Algorithms
1. **Prompt Engineering**
   - Structured prompt generation
   - Error context embedding
   - Code snippet inclusion
   - Multi-step instruction format

2. **Response Parsing**
   - JSON extraction from markdown code blocks
   - Multi-format response handling
   - Nested JSON structure parsing
   - Fallback parsing with regex

3. **Response Validation**
   - Corrected code comparison with original
   - Fix validation (check if errors are actually fixed)
   - Explanation completeness checking
   - Error count matching

### Error Analysis Workflow
1. **Compilation Phase**
   - Code → Compiler → Error extraction → Error parsing

2. **Execution Phase** (if compilation succeeds)
   - Compiled code → Execution → Output capture → Runtime error detection

3. **Output Analysis Phase** (if execution succeeds)
   - Actual output → Expected output → Comparison → Difference detection

4. **LLM Explanation Phase**
   - Errors + Code + Output analysis → LLM API → Explanation parsing → Validation

---

## Development & Build Tools

### Frontend Build Tools
- **Vite** - Fast build tool and dev server
- **ESBuild** (via Vite) - JavaScript/TypeScript bundler
- **SWC** (via @vitejs/plugin-react-swc) - Fast TypeScript/JavaScript compiler

### Backend Tools
- **Python pip** - Package management
- **Virtual Environment** (recommended) - Python environment isolation

### Version Control
- **Git** - Version control system
- **.gitignore** - Excludes node_modules, .env, build artifacts

---

## Deployment & Infrastructure

### Runtime Requirements
- **Node.js** - For frontend (if running separately)
- **Python 3.x** - For backend
- **GCC** - Must be installed on system for C compilation
- **JDK** - Must be installed on system for Java compilation

### Configuration Files
- **package.json** - Frontend dependencies and scripts
- **requirements.txt** - Backend Python dependencies
- **.env** - Environment variables (API keys, configuration)
- **vite.config.ts** - Vite configuration
- **tailwind.config.ts** - Tailwind CSS configuration
- **tsconfig.json** - TypeScript configuration
- **eslint.config.js** - ESLint configuration
- **postcss.config.js** - PostCSS configuration

### Scripts
- **Frontend**: `npm run dev`, `npm run build`, `npm run lint`
- **Backend**: `python main.py`, `uvicorn main:app`, custom run scripts

---

## Security Features

1. **API Key Management**
   - Stored in `.env` file (not committed to git)
   - Environment variable loading

2. **Input Validation**
   - Pydantic models for request validation
   - Type checking at API boundaries

3. **Execution Security**
   - Timeout limits prevent infinite loops
   - Output size limits prevent memory exhaustion
   - Temporary file cleanup
   - Isolated execution environment

4. **CORS Configuration**
   - Configurable CORS middleware
   - Development: Allow all origins
   - Production: Should restrict to specific origins

---

## Testing & Quality Assurance

### Code Quality Tools
- **ESLint** - JavaScript/TypeScript linting
- **TypeScript** - Static type checking
- **Pydantic** - Runtime type validation (backend)

### Testing
- Custom test scripts in backend:
  - `test_api.py` - API endpoint testing
  - `test_gemini_api.py` - Gemini API testing
  - `check_api_key.py` - API key validation

---

## Summary Statistics

- **Frontend Dependencies**: 60+ npm packages
- **Backend Dependencies**: 8 Python packages
- **Supported Languages**: C, Java
- **API Integrations**: Google Gemini AI
- **Compiler Integrations**: GCC, Javac
- **Total Technologies**: 80+ (including all UI components, utilities, and tools)
