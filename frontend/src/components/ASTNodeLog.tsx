'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TraceStep } from '@/lib/api';

interface ASTNodeLogProps {
  visibleSteps: TraceStep[];
  currentStep: TraceStep | null;
}

// Define node colors based on AST node type
const getNodeColor = (nodeType: string): string => {
  switch (nodeType) {
    case 'Program':
      return '#3b82f6'; // blue
    case 'Assignment':
      return '#10b981'; // emerald  
    case 'BinaryOp':
      return '#f59e0b'; // amber
    case 'Number':
    case 'Float':
      return '#8b5cf6'; // violet
    case 'Identifier':
      return '#06b6d4'; // cyan
    default:
      return '#6b7280'; // gray
  }
};

export function ASTNodeLog({ visibleSteps, currentStep }: ASTNodeLogProps) {
  // Filter to AST node creation steps
  const astSteps = visibleSteps.filter(step => 
    step.phase === 'parsing' && 
    step.state.action === 'create_ast_node' &&
    step.state.ast_node
  );

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          AST Node Creation Log
        </h3>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          <AnimatePresence>
            {astSteps.map((step, index) => (
              <motion.div
                key={`step-${step.step_id}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`p-2 rounded border text-sm ${
                  currentStep?.step_id === step.step_id
                    ? 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800'
                    : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span 
                    className="px-2 py-1 rounded text-xs font-semibold text-white"
                    style={{ backgroundColor: getNodeColor(
                      typeof step.state.ast_node === 'object' && step.state.ast_node !== null && 'type' in step.state.ast_node 
                        ? step.state.ast_node.type 
                        : 'Unknown'
                    ) }}
                  >
                    {typeof step.state.ast_node === 'object' && step.state.ast_node !== null && 'type' in step.state.ast_node 
                      ? step.state.ast_node.type 
                      : 'Unknown'}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Step {step.step_id}
                  </span>
                </div>
                <div className="text-gray-700 dark:text-gray-300 mt-1">
                  {step.description}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          AST Node Types
        </h3>
        <div className="grid grid-cols-1 gap-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-500"></div>
            <span>Program - Root of the AST</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500"></div>
            <span>Assignment - Variable assignment</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-amber-500"></div>
            <span>BinaryOp - Binary operations</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-violet-500"></div>
            <span>Number/Float - Literals</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-cyan-500"></div>
            <span>Identifier - Variables</span>
          </div>
        </div>
      </div>
    </div>
  );
}