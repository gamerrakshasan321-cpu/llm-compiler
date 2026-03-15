import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Code2, Bug } from "lucide-react";

interface HeroProps {
  onStartDebugging: () => void;
}

const Hero = ({ onStartDebugging }: HeroProps) => {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 15}s`,
    size: Math.random() * 4 + 2,
  }));

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 gradient-bg opacity-90" />
      
      {/* Grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(hsl(var(--foreground) / 0.1) 1px, transparent 1px),
            linear-gradient(90deg, hsl(var(--foreground) / 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Floating particles */}
      <div className="floating-particles">
        {particles.map((particle) => (
          <div
            key={particle.id}
            className="particle"
            style={{
              left: particle.left,
              animationDelay: particle.delay,
              width: particle.size,
              height: particle.size,
            }}
          />
        ))}
      </div>

      {/* Glowing orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse-glow" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent/20 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: '1s' }} />

      {/* Content */}
      <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-card/20 backdrop-blur-lg border border-primary-foreground/20 mb-8 animate-fade-in">
          <Sparkles className="w-4 h-4 text-primary-foreground" />
          <span className="text-sm font-medium text-primary-foreground">AI-Powered Code Analysis</span>
        </div>

        {/* Main heading */}
        <h1 className="text-5xl md:text-7xl font-bold text-primary-foreground mb-6 animate-slide-up">
          AI Compiler
          <br />
          <span className="relative">
            Debugging Assistant
            <svg
              className="absolute -bottom-2 left-0 w-full"
              viewBox="0 0 400 12"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M2 10C50 2 100 2 200 6C300 10 350 6 398 2"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                className="text-accent"
              />
            </svg>
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-primary-foreground/80 mb-12 max-w-2xl mx-auto animate-slide-up" style={{ animationDelay: '0.2s' }}>
          Understand compile-time, runtime, and logical errors instantly with intelligent AI explanations
        </p>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-4 mb-12 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-destructive/20 border border-destructive/30 backdrop-blur-sm">
            <Bug className="w-4 h-4 text-destructive-foreground" />
            <span className="text-sm text-primary-foreground">Compile Errors</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-warning/20 border border-warning/30 backdrop-blur-sm">
            <Code2 className="w-4 h-4 text-warning-foreground" />
            <span className="text-sm text-primary-foreground">Runtime Errors</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-success/20 border border-success/30 backdrop-blur-sm">
            <Sparkles className="w-4 h-4 text-success-foreground" />
            <span className="text-sm text-primary-foreground">Logic Analysis</span>
          </div>
        </div>

        {/* CTA Button */}
        <div className="animate-slide-up" style={{ animationDelay: '0.4s' }}>
          <Button 
            variant="glass" 
            size="xl" 
            onClick={onStartDebugging}
            className="group bg-primary-foreground text-primary hover:bg-primary-foreground/90"
          >
            Start Debugging
            <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </Button>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  );
};

export default Hero;
