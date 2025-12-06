'use client';

import { ExecutedASTNode } from '@/lib/api';
import { ExecutionTreeVisualizer } from './ExecutionTreeVisualizer';

interface DirectExecutionPhaseProps {
  executedAst?: ExecutedASTNode;
  variables?: Record<string, number>;
  output?: (number | string)[];
  identifierMapping?: Record<string, string>;
  sourceCode?: string;
}

export function DirectExecutionPhase({
  executedAst,
  variables,
  output,
  identifierMapping,
  sourceCode,
}: DirectExecutionPhaseProps) {
  return (
    <div className="space-y-4">
      {/* Source Code Card */}
      {sourceCode && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
          <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
            Source Code
          </h3>
          <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded border">
            <pre className="font-mono text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
              {sourceCode}
            </pre>
          </div>
        </div>
      )}

      {/* Execution Tree */}
      <ExecutionTreeVisualizer 
        executedAst={executedAst} 
        identifierMapping={identifierMapping}
      />
      
      {/* Symbol Table Panel */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Symbol Table (Final Variable Values)
        </h3>
        <div className="flex flex-wrap gap-2">
          {variables && Object.keys(variables).length > 0 ? (
            Object.entries(variables).map(([name, value]) => {
              const normalizedName = identifierMapping?.[name] || name;
              return (
                <div 
                  key={name} 
                  className="bg-gray-50 dark:bg-gray-900 px-3 py-2 rounded border flex items-center gap-2"
                >
                  <span className="font-mono text-blue-600 dark:text-blue-400 font-semibold">
                    {normalizedName} ({name.toUpperCase()})
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">=</span>
                  <span className="font-mono text-purple-600 dark:text-purple-400 font-semibold">
                    {typeof value === 'number' && !Number.isInteger(value) 
                      ? value.toFixed(2) 
                      : value}
                  </span>
                </div>
              );
            })
          ) : (
            <span className="text-gray-500 dark:text-gray-400 text-sm">
              No variables defined
            </span>
          )}
        </div>
      </div>
      
      {/* Output Panel */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Program Output
        </h3>
        <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm min-h-[60px]">
          {output && output.length > 0 ? (
            output.map((val, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-gray-500">&gt;</span>
                <span>
                  {typeof val === 'number' && !Number.isInteger(val) 
                    ? val.toFixed(2) 
                    : String(val)}
                </span>
              </div>
            ))
          ) : (
            <span className="text-gray-500">No output (no write statements executed)</span>
          )}
        </div>
      </div>
    </div>
  );
}
