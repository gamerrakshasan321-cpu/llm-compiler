import { cn } from "@/lib/utils";

interface LanguageSelectorProps {
  selectedLanguage: 'C' | 'Java';
  onLanguageChange: (language: 'C' | 'Java') => void;
}

const LanguageSelector = ({ selectedLanguage, onLanguageChange }: LanguageSelectorProps) => {
  return (
    <div className="inline-flex items-center p-1 rounded-xl bg-secondary border border-border">
      <button
        onClick={() => onLanguageChange('C')}
        className={cn(
          "px-6 py-2 rounded-lg font-medium text-sm transition-all duration-300",
          selectedLanguage === 'C'
            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        <span className="flex items-center gap-2">
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2v-2zm0-8h2v6h-2V8z"/>
          </svg>
          C
        </span>
      </button>
      <button
        onClick={() => onLanguageChange('Java')}
        className={cn(
          "px-6 py-2 rounded-lg font-medium text-sm transition-all duration-300",
          selectedLanguage === 'Java'
            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        <span className="flex items-center gap-2">
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor">
            <path d="M8.851 18.56s-.917.534.653.714c1.902.218 2.874.187 4.969-.211 0 0 .552.346 1.321.646-4.699 2.013-10.633-.118-6.943-1.149M8.276 15.933s-1.028.761.542.924c2.032.209 3.636.227 6.413-.308 0 0 .384.389.987.602-5.679 1.661-12.007.13-7.942-1.218M13.116 11.475c1.158 1.333-.304 2.533-.304 2.533s2.939-1.518 1.589-3.418c-1.261-1.772-2.228-2.652 3.007-5.688 0-.001-8.216 2.051-4.292 6.573"/>
          </svg>
          Java
        </span>
      </button>
    </div>
  );
};

export default LanguageSelector;
