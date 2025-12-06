'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiClient, type ICGResponse, type ICGInstruction, type OptimizationResponse, type CodeGenResponse, type AssemblyInstruction } from '@/lib/api';

interface ICGPhaseProps {
  sourceCode: string;
}

export function ICGPhase({ sourceCode }: ICGPhaseProps) {
  const [icgData, setIcgData] = useState<ICGResponse | null>(null);
  const [optimizationData, setOptimizationData] = useState<OptimizationResponse | null>(null);
  const [codeGenData, setCodeGenData] = useState<CodeGenResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const generateAll = async () => {
      if (!sourceCode.trim()) return;

      setIsLoading(true);
      setError(null);

      try {
        // Fetch all three in parallel
        const [icgResponse, optimizationResponse, codeGenResponse] = await Promise.all([
          apiClient.generateICG(sourceCode),
          apiClient.optimizeCode(sourceCode),
          apiClient.generateCode(sourceCode),
        ]);

        setIcgData(icgResponse);
        setOptimizationData(optimizationResponse);
        setCodeGenData(codeGenResponse);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to generate code');
      } finally {
        setIsLoading(false);
      }
    };

    generateAll();
  }, [sourceCode]);

  const getTokenColor = (token: string): string => {
    if (token.startsWith('#')) return 'text-pink-400'; // Literals
    if (token.startsWith('temp')) return 'text-green-400'; // Temps
    if (token.includes('(f)')) return 'text-cyan-400'; // Float annotation
    if (token.startsWith('id') && /^id\d+/.test(token)) return 'text-blue-400'; // Normalized identifiers
    if (token.startsWith('L') && /^L\d+/.test(token)) return 'text-orange-400'; // Labels
    if (['read', 'write', 'goto', 'if_false', 'label', 'int2float'].includes(token))
      return 'text-purple-400'; // Keywords
    if (['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '='].includes(token))
      return 'text-yellow-400'; // Operators
    return 'text-gray-400'; // Other
  };

  const getAssemblyTokenColor = (token: string): string => {
    // Registers
    if (token === 'R1' || token === 'R2') return 'text-red-400';
    // Instructions
    if (['LOAD', 'LOADF', 'STR', 'STRF', 'ADD', 'ADDF', 'SUB', 'SUBF', 'MUL', 'MULF', 'DIV', 'DIVF', 'MOD', 'MODF'].includes(token))
      return 'text-purple-400';
    // Literals
    if (token.startsWith('#')) return 'text-pink-400';
    // Float annotation
    if (token.includes('(f)')) return 'text-cyan-400';
    // Normalized identifiers
    if (token.startsWith('id') && /^id\d+/.test(token)) return 'text-blue-400';
    // Temps
    if (token.startsWith('temp')) return 'text-green-400';
    return 'text-gray-400';
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

  const highlightAssemblyTokens = (instruction: string) => {
    const tokens = instruction.split(/(\s+|[,])/);
    return (
      <>
        {tokens.map((token, idx) => {
          if (token.trim() === '') return <span key={idx}>{token}</span>;
          return (
            <span key={idx} className={getAssemblyTokenColor(token)}>
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
          Code Generation & Optimization
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Three-address code with optimization to reduce unnecessary temporaries
        </p>
      </div>

      {/* Source Code */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
          Source Code
        </h3>
        <div className="bg-gray-900 p-4 rounded-lg font-mono text-sm overflow-x-auto">
          <pre className="text-gray-100 whitespace-pre-wrap">{sourceCode}</pre>
        </div>
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

      {/* Side-by-side Code Comparison */}
      {optimizationData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Original ICG */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
              Before Optimization ({icgData.instructions.length} instructions)
            </h3>
            <div className="bg-gray-900 p-3 rounded-lg font-mono text-sm overflow-x-auto max-h-96 overflow-y-auto">
              {icgData.instructions.map((inst: ICGInstruction, idx: number) => (
                <div key={idx} className="text-gray-100">
                  <span className="text-gray-500 mr-3">{idx + 1}.</span>
                  {highlightTokens(inst.instruction)}
                </div>
              ))}
            </div>
          </div>

          {/* Optimized ICG */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-green-500/30">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
              After Optimization ({optimizationData.optimized_instructions.length} instructions)
            </h3>
            <div className="bg-gray-900 p-3 rounded-lg font-mono text-sm overflow-x-auto max-h-96 overflow-y-auto">
              {optimizationData.optimized_instructions.map((inst: ICGInstruction, idx: number) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="text-gray-100"
                >
                  <span className="text-gray-500 mr-3">{idx + 1}.</span>
                  {highlightTokens(inst.instruction)}
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Generated Assembly Code */}
      {codeGenData && codeGenData.success && codeGenData.assembly_instructions.length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-purple-500/30">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Generated Assembly Code ({codeGenData.assembly_instructions.length} instructions)
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Assembly-like code generated from optimized TAC. Target: 2-register architecture (R1, R2)
          </p>
          <div className="bg-gray-900 p-4 rounded-lg font-mono text-sm overflow-x-auto max-h-96 overflow-y-auto">
            {codeGenData.assembly_instructions.map((inst: AssemblyInstruction, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.03 }}
                className="text-gray-100"
              >
                <span className="text-gray-500 mr-3 select-none">{String(idx + 1).padStart(2, ' ')}.</span>
                {highlightAssemblyTokens(inst.instruction)}
              </motion.div>
            ))}
          </div>

          {/* Assembly Instruction Reference */}
          <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-700/50 rounded-lg">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Instruction Reference
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              <div>
                <span className="text-purple-400 font-mono">LOAD/LOADF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Load int/float</span>
              </div>
              <div>
                <span className="text-purple-400 font-mono">STR/STRF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Store int/float</span>
              </div>
              <div>
                <span className="text-purple-400 font-mono">ADD/ADDF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Add int/float</span>
              </div>
              <div>
                <span className="text-purple-400 font-mono">SUB/SUBF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Subtract int/float</span>
              </div>
              <div>
                <span className="text-purple-400 font-mono">MUL/MULF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Multiply int/float</span>
              </div>
              <div>
                <span className="text-purple-400 font-mono">DIV/DIVF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Divide int/float</span>
              </div>
              <div>
                <span className="text-purple-400 font-mono">MOD/MODF</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Modulo int/float</span>
              </div>
              <div>
                <span className="text-red-400 font-mono">R1, R2</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">- Registers</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Instructions Table - Original */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border overflow-hidden">
        <div className="p-4 bg-gray-50 dark:bg-gray-700">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">
            Original Three-Address Code (Detailed View)
          </h3>
        </div>
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

      {/* Legend */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
            <span className="text-cyan-400 font-mono">id1(f)</span>
            <span className="text-sm text-gray-600 dark:text-gray-400">Float annotation</span>
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

      {/* Optimization Statistics - at the bottom */}
      {optimizationData?.stats && (
        <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg p-6 border border-blue-700/30">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Optimization Results
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400">Instructions Saved</div>
              <div className="text-2xl font-bold text-green-400">
                {optimizationData.stats.instructions_saved}
              </div>
            </div>
            <div className="bg-white/10 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400">Reduction</div>
              <div className="text-2xl font-bold text-blue-400">
                {optimizationData.stats.reduction_percentage.toFixed(1)}%
              </div>
            </div>
            <div className="bg-white/10 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400">Original Count</div>
              <div className="text-2xl font-bold text-gray-400">
                {optimizationData.stats.original_instruction_count}
              </div>
            </div>
            <div className="bg-white/10 dark:bg-gray-800/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400">Optimized Count</div>
              <div className="text-2xl font-bold text-purple-400">
                {optimizationData.stats.optimized_instruction_count}
              </div>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
            <div className="bg-white/5 dark:bg-gray-800/30 rounded p-2">
              <div className="text-gray-500 dark:text-gray-400">int2float inlined</div>
              <div className="text-lg font-semibold text-cyan-400">
                {optimizationData.stats.int2float_inlined}
              </div>
            </div>
            <div className="bg-white/5 dark:bg-gray-800/30 rounded p-2">
              <div className="text-gray-500 dark:text-gray-400">Temps eliminated</div>
              <div className="text-lg font-semibold text-green-400">
                {optimizationData.stats.temps_eliminated}
              </div>
            </div>
            <div className="bg-white/5 dark:bg-gray-800/30 rounded p-2">
              <div className="text-gray-500 dark:text-gray-400">Copies propagated</div>
              <div className="text-lg font-semibold text-yellow-400">
                {optimizationData.stats.copies_propagated}
              </div>
            </div>
            <div className="bg-white/5 dark:bg-gray-800/30 rounded p-2">
              <div className="text-gray-500 dark:text-gray-400">Algebraic simplifications</div>
              <div className="text-lg font-semibold text-orange-400">
                {optimizationData.stats.algebraic_simplifications}
              </div>
            </div>
            <div className="bg-white/5 dark:bg-gray-800/30 rounded p-2">
              <div className="text-gray-500 dark:text-gray-400">Dead code removed</div>
              <div className="text-lg font-semibold text-red-400">
                {optimizationData.stats.dead_code_eliminated}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
