'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiClient, type ICGResponse, type ICGInstruction } from '@/lib/api';

interface ICGPhaseProps {
  sourceCode: string;
}

export function ICGPhase({ sourceCode }: ICGPhaseProps) {
  const [icgData, setIcgData] = useState<ICGResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const generateICG = async () => {
      if (!sourceCode.trim()) return;

      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.generateICG(sourceCode);
        setIcgData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to generate ICG');
      } finally {
        setIsLoading(false);
      }
    };

    generateICG();
  }, [sourceCode]);

  const getTokenColor = (token: string): string => {
    if (token.startsWith('#')) return 'text-pink-400'; // Literals
    if (token.startsWith('temp')) return 'text-green-400'; // Temps
    if (token.startsWith('id') && /^id\d+/.test(token)) return 'text-blue-400'; // Normalized identifiers
    if (token.startsWith('L') && /^L\d+/.test(token)) return 'text-orange-400'; // Labels
    if (['read', 'write', 'goto', 'if_false', 'label', 'int2float'].includes(token))
      return 'text-purple-400'; // Keywords
    if (['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '='].includes(token))
      return 'text-yellow-400'; // Operators
    return 'text-gray-400'; // Other
  };

  const highlightTokens = (instruction: string) => {
    const tokens = instruction.split(/(\s+|[=():;,])/);
    return (
      <>
        {tokens.map((token, idx) => {
          if (token.trim() === '') return <span key={idx}>{token}</span>;
          return (
            <span key={idx} className={getTokenColor(token)}>
              {token}
            </span>
          );
        })}
      </>
    );
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border">
        <div className="text-center text-gray-600 dark:text-gray-400">
          Generating intermediate code...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg border border-red-200 dark:border-red-800">
        <div className="text-red-800 dark:text-red-200">{error}</div>
      </div>
    );
  }

  if (!icgData) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border">
        <div className="text-center text-gray-600 dark:text-gray-400">
          Enter code to generate intermediate code
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Intermediate Code Generation (ICG)
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Three-address code representation of your program
        </p>
      </div>

      {/* Identifier Mapping */}
      {Object.keys(icgData.identifier_mapping).length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Identifier Mapping
          </h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(icgData.identifier_mapping).map(([original, normalized]) => (
              <div
                key={original}
                className="bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-md border border-blue-200 dark:border-blue-800"
              >
                <span className="font-mono text-gray-900 dark:text-gray-100">{original}</span>
                <span className="mx-2 text-gray-500 dark:text-gray-400">→</span>
                <span className="font-mono text-blue-600 dark:text-blue-400">{normalized}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
          <div className="text-sm text-gray-600 dark:text-gray-400">Instructions</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {icgData.instructions.length}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
          <div className="text-sm text-gray-600 dark:text-gray-400">Temp Variables</div>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {icgData.temp_count}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
          <div className="text-sm text-gray-600 dark:text-gray-400">Labels</div>
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {icgData.label_count}
          </div>
        </div>
      </div>

      {/* Instructions Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Line
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Operation
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Arg1
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Arg2
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Result
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  Instruction
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {icgData.instructions.map((inst: ICGInstruction, idx: number) => (
                <motion.tr
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {idx + 1}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono">
                    <span className="text-purple-600 dark:text-purple-400">{inst.op}</span>
                  </td>
                  <td className="px-4 py-3 text-sm font-mono">
                    {inst.arg1 && (
                      <span className={getTokenColor(inst.arg1)}>{inst.arg1}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono">
                    {inst.arg2 && (
                      <span className={getTokenColor(inst.arg2)}>{inst.arg2}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono">
                    {inst.result && (
                      <span className={getTokenColor(inst.result)}>{inst.result}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-900 dark:text-gray-100">
                    {highlightTokens(inst.instruction)}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Code Listing */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
          Three-Address Code
        </h3>
        <div className="bg-gray-900 p-4 rounded-lg font-mono text-sm overflow-x-auto">
          {icgData.instructions.map((inst: ICGInstruction, idx: number) => (
            <div key={idx} className="text-gray-100">
              <span className="text-gray-500 mr-4">{idx + 1}.</span>
              {highlightTokens(inst.instruction)}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div className="flex items-center gap-2">
            <span className="text-pink-400 font-mono">#5</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Literals</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-400 font-mono">temp1</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Temp variables</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-blue-400 font-mono">id1</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Identifiers</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-orange-400 font-mono">L1</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Labels</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-purple-400 font-mono">read</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Operations</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-yellow-400 font-mono">+</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Operators</span>
          </div>
        </div>
      </div>
    </div>
  );
}
