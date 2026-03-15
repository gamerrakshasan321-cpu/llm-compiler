import { useNavigate } from "react-router-dom";
import Hero from "@/components/Hero";

const Index = () => {
  const navigate = useNavigate();

  const goToWorkspace = () => {
    navigate("/workspace");
  };

  return (
    <main className="min-h-screen bg-background">
      <Hero onStartDebugging={goToWorkspace} />
    </main>
  );
};

export default Index;
