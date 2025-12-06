'use client';

import { motion } from 'framer-motion';
import { TraceStep, ASTNode } from '@/lib/api';
import { AnalyzedASTVisualizer } from './AnalyzedASTVisualizer';

interface SemanticAnalysisPhaseProps {
  visibleSteps: TraceStep[];
  currentStep: TraceStep | null;
  analyzedAst?: ASTNode;
  identifierMapping?: Record<string, string>;
}

interface SemanticStep {
  action: string;
  description: string;
  details: string;
}

export function SemanticAnalysisPhase({ visibleSteps, currentStep, analyzedAst, identifierMapping }: SemanticAnalysisPhaseProps) {
  const semanticSteps = visibleSteps.filter(step => step.phase === 'semantic-analysis');
  
  const semanticTrace: SemanticStep[] = semanticSteps.map(step => ({
    action: String(step.state.action || 'unknown'),
    description: step.description,
    details: JSON.stringify(step.state, null, 2),
  }));

  const getActionColor = (action: string) => {
    const colorMap: Record<string, string> = {
      'start_analysis': 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
      'analyze_statement': 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200',
      'start_assignment_analysis': 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
      'update_symbol_table': 'bg-cyan-100 dark:bg-cyan-900 text-cyan-800 dark:text-cyan-200',
      'analyze_expression': 'bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200',
      'start_binary_op_analysis': 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200',
      'check_operand_types': 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
      'coercion_needed': 'bg-pink-100 dark:bg-pink-900 text-pink-800 dark:text-pink-200',
      'create_coercion_node': 'bg-rose-100 dark:bg-rose-900 text-rose-800 dark:text-rose-200',
      'no_coercion': 'bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200',
      'complete_analysis': 'bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-200',
    };
    return colorMap[action] || 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200';
  };

  return (
    <div className="space-y-6">
      {/* Top: Analyzed AST Tree - Full width */}
      <div className="w-full">
        <AnalyzedASTVisualizer analyzedAst={analyzedAst} identifierMapping={identifierMapping} />
      </div>

      {/* Bottom: Semantic Analysis Trace */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Semantic Analysis Trace
        </h3>
        
        <div className="space-y-2">
          {semanticTrace.length > 0 ? (
            semanticTrace.map((step, index) => {
              const stepData = semanticSteps[index];
              const isCurrentStep = currentStep?.step_id === stepData.step_id;
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ 
                    opacity: 1, 
                    x: 0,
                    scale: isCurrentStep ? 1.02 : 1,
                  }}
                  transition={{ delay: index * 0.05 }}
                  className={`p-3 rounded border ${
                    isCurrentStep 
                      ? 'border-yellow-400 dark:border-yellow-500 bg-yellow-50 dark:bg-yellow-950 ring-2 ring-yellow-400 dark:ring-yellow-500' 
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xs font-mono text-gray-500 dark:text-gray-400 mt-1">
                      {stepData.step_id}
                    </span>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getActionColor(step.action)}`}>
                          {step.action}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                        {step.description}
                      </div>

                      {isCurrentStep && stepData.state && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mt-2 p-2 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700"
                        >
                          <div className="text-xs font-mono text-gray-600 dark:text-gray-400">
                            {Object.entries(stepData.state).map(([key, value]) => (
                              <div key={key} className="mb-1">
                                <span className="font-semibold">{key}:</span>{' '}
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No semantic analysis steps yet. Run the compiler to see type checking and coercion.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
