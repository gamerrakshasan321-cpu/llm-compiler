import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { HelpCircle } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface TestCaseInputProps {
  inputData: string;
  expectedOutput: string;
  onInputDataChange: (value: string) => void;
  onExpectedOutputChange: (value: string) => void;
}

const TestCaseInput = ({
  inputData,
  expectedOutput,
  onInputDataChange,
  onExpectedOutputChange,
}: TestCaseInputProps) => {
  return (
    <div className="space-y-4 p-4 rounded-xl border border-border bg-card">
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-semibold text-foreground">Test Cases</h3>
        <Tooltip>
          <TooltipTrigger asChild>
            <HelpCircle className="w-4 h-4 text-muted-foreground cursor-help" />
          </TooltipTrigger>
          <TooltipContent>
            <p className="max-w-xs text-xs">
              Provide input data and expected output to detect logical errors in your program
            </p>
          </TooltipContent>
        </Tooltip>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="input-data" className="text-xs text-muted-foreground">
            Input Data
          </Label>
          <Textarea
            id="input-data"
            value={inputData}
            onChange={(e) => onInputDataChange(e.target.value)}
            placeholder="Enter test input..."
            className="h-24 font-mono text-sm resize-none bg-secondary/50 border-border focus:border-primary"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="expected-output" className="text-xs text-muted-foreground">
            Expected Output
          </Label>
          <Textarea
            id="expected-output"
            value={expectedOutput}
            onChange={(e) => onExpectedOutputChange(e.target.value)}
            placeholder="Enter expected output..."
            className="h-24 font-mono text-sm resize-none bg-secondary/50 border-border focus:border-primary"
          />
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Used to detect logical errors by comparing actual output with expected output
      </p>
    </div>
  );
};

export default TestCaseInput;
