import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { StepByStepVisualizer } from '@/components/StepByStepVisualizer';

export default function VisualizePage() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Navigation */}
      <div className="p-4 border-b border-gray-800">
        <div className="max-w-7xl mx-auto">
          <Link 
            href="/"
            className="inline-flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Lexer/Parser
          </Link>
        </div>
      </div>
      
      {/* Main Content */}
      <StepByStepVisualizer />
    </div>
  );
}