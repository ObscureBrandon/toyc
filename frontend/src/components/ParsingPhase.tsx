'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { TraceStep } from '@/lib/api';

interface ParsingPhaseProps {
  visibleSteps: TraceStep[];
  currentStep: TraceStep | null;
}

interface ParseStep {
  rule: string;
  action: string;
  currentToken: string;
  lookahead?: string;
  stackDescription?: string;
}

export function ParsingPhase({ visibleSteps, currentStep }: ParsingPhaseProps) {
  // Filter to parsing phase steps
  const parsingSteps = visibleSteps.filter(step => step.phase === 'parsing');
  
  // Extract parse steps for the parsing trace
  const parseTrace: ParseStep[] = parsingSteps.map(step => ({
    rule: step.state.grammar_rule || 'unknown',
    action: step.state.action || step.description,
    currentToken: step.state.current_token || '',
    lookahead: step.state.peek_token || '',
    stackDescription: step.state.stack_description || '',
  }));

  const getRuleColor = (rule: string) => {
    const colorMap: Record<string, string> = {
      'program': 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
      'statement': 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
      'expression': 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200',
      'assignment': 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200',
      'term': 'bg-pink-100 dark:bg-pink-900 text-pink-800 dark:text-pink-200',
      'factor': 'bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200',
      'primary': 'bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-200',
    };
    return colorMap[rule] || 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200';
  };

  const getActionColor = (action: string) => {
    if (action.includes('enter') || action.includes('start')) {
      return 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800';
    }
    if (action.includes('exit') || action.includes('end')) {
      return 'bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800';
    }
    if (action.includes('consume') || action.includes('match')) {
      return 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800';
    }
    return 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700';
  };

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Parser State
        </h3>
        {currentStep && currentStep.phase === 'parsing' ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Current Rule:</span>
              <span className={`px-2 py-1 rounded text-xs ${getRuleColor(currentStep.state.grammar_rule || '')}`}>
                {currentStep.state.grammar_rule || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Current Token:</span>
              <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">
                {currentStep.state.current_token || 'N/A'}
              </span>
            </div>
            {currentStep.state.peek_token && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Lookahead:</span>
                <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">
                  {currentStep.state.peek_token}
                </span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Action:</span>
              <span className="text-right flex-1 ml-2">
                {currentStep.state.action || currentStep.description}
              </span>
            </div>
          </div>
        ) : (
          <div className="text-gray-500 dark:text-gray-400 text-sm">
            Waiting for parsing step...
          </div>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Parse Trace
        </h3>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          <AnimatePresence>
            {parseTrace.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`p-3 rounded border ${getActionColor(step.action)}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getRuleColor(step.rule)}`}>
                    {step.rule}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Step {index + 1}
                  </span>
                </div>
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  {step.action}
                </div>
                {step.currentToken && (
                  <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Token: <span className="font-mono">{step.currentToken}</span>
                    {step.lookahead && (
                      <span className="ml-2">
                        | Lookahead: <span className="font-mono">{step.lookahead}</span>
                      </span>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {currentStep && currentStep.state.stack_description && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
          <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
            Parse Stack
          </h3>
          <div className="text-sm font-mono bg-gray-50 dark:bg-gray-900 p-2 rounded">
            {currentStep.state.stack_description}
          </div>
        </div>
      )}
    </div>
  );
}