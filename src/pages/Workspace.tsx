import Workspace from "@/components/Workspace";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

const WorkspacePage = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-lg">
        <div className="max-w-[1800px] mx-auto px-4 md:px-8 py-4 flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div className="h-6 w-px bg-border" />
          <h1 className="text-lg font-semibold gradient-text">
            AI Compiler Debugging Assistant
          </h1>
        </div>
      </header>

      <Workspace />
    </main>
  );
};

export default WorkspacePage;
