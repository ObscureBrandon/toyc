"use client";

import { useState } from "react";
import { apiClient, type ICGResponse } from "@/lib/api";

export default function ICGVisualizer() {
  const placeholderCode = `x := 5 + 3 * 2;
if (x > 10) then
  write x;
end`;

  const [sourceCode, setSourceCode] = useState(placeholderCode);
  const [result, setResult] = useState<ICGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    const codeToProcess = sourceCode.trim() || placeholderCode;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.generateICG(codeToProcess);
      setResult(response);
      if (!response.success) {
        setError(response.error || "Failed to generate ICG");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate ICG");
    } finally {
      setLoading(false);
    }
  };

  const formatInstruction = (instr: ICGResponse["instructions"][0]): string => {
    if (instr.label) {
      return `label ${instr.label}:`;
    } else if (instr.op === "assign") {
      return `${instr.result} = ${instr.arg1}`;
    } else if (instr.op === "goto") {
      return `goto ${instr.arg1}`;
    } else if (instr.op === "if_false") {
      return `if_false ${instr.arg1} goto ${instr.arg2}`;
    } else if (instr.op === "if_true") {
      return `if_true ${instr.arg1} goto ${instr.arg2}`;
    } else if (instr.op === "read") {
      return `read ${instr.arg1}`;
    } else if (instr.op === "write") {
      return `write ${instr.arg1}`;
    } else if (instr.op === "int2float") {
      return `${instr.result} = int2float(${instr.arg1})`;
    } else if (instr.arg2) {
      return `${instr.result} = ${instr.arg1} ${instr.op} ${instr.arg2}`;
    } else {
      return `${instr.result} = ${instr.op} ${instr.arg1}`;
    }
  };

  const getInstructionColor = (instr: ICGResponse["instructions"][0]): string => {
    if (instr.label) {
      return "text-orange-400"; // Labels
    } else if (instr.op === "assign") {
      return "text-green-400"; // Assignments
    } else if (instr.op === "goto" || instr.op === "if_false" || instr.op === "if_true") {
      return "text-yellow-400"; // Control flow
    } else if (instr.op === "read" || instr.op === "write") {
      return "text-purple-400"; // I/O
    } else if (instr.op === "int2float") {
      return "text-pink-400"; // Type conversion
    } else {
      return "text-blue-400"; // Arithmetic
    }
  };

  const getTokenColor = (token: string): string => {
    if (token.startsWith("#")) {
      return "text-pink-300"; // Literals
    } else if (token.startsWith("temp")) {
      return "text-green-300"; // Temps
    } else if (token.startsWith("L")) {
      return "text-orange-300"; // Labels
    } else {
      return "text-blue-300"; // Variables
    }
  };

  const highlightTokens = (instruction: string) => {
    const tokens = instruction.split(/(\s+|[=():;,])/);
    return (
      <>
        {tokens.map((token, idx) => {
          if (token.trim() === "") return <span key={idx}>{token}</span>;
          return (
            <span key={idx} className={getTokenColor(token)}>
              {token}
            </span>
          );
        })}
      </>
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-7xl mx-auto p-6">
        <h1 className="text-4xl font-bold mb-8 text-center text-white">
          ToyC ICG Generator
        </h1>
        <p className="text-center text-gray-400 mb-8">
          Three-Address Code (Intermediate Code Generation)
        </p>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2 text-gray-300">
            Source Code:
          </label>
          <textarea
            value={sourceCode}
            onChange={(e) => setSourceCode(e.target.value)}
            className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg font-mono text-sm text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={8}
            placeholder={placeholderCode}
          />
        </div>

        <div className="mb-6 flex gap-4">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {loading ? "Generating..." : "Generate ICG"}
          </button>

          <button
            onClick={() => {
              setSourceCode(placeholderCode);
              setResult(null);
              setError(null);
            }}
            className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 font-medium transition-colors"
          >
            Reset
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-700/30 rounded-lg">
            <p className="text-red-300 font-medium">Error:</p>
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {result && result.success && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Three-Address Code Instructions
              </h2>
              <div className="bg-gray-800/50 rounded-lg overflow-hidden shadow-sm border border-gray-700/30">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-700/50">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Line
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Operation
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Arg1
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Arg2
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Result
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Instruction
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.instructions.map((instr, idx) => (
                        <tr
                          key={idx}
                          className="border-b border-gray-700/30 hover:bg-gray-700/20"
                        >
                          <td className="py-3 px-4 font-mono text-gray-400">
                            {idx + 1}
                          </td>
                          <td className="py-3 px-4 font-mono font-medium text-gray-200">
                            {instr.label ? "label" : instr.op}
                          </td>
                          <td className="py-3 px-4 font-mono text-gray-300">
                            {instr.arg1 || "-"}
                          </td>
                          <td className="py-3 px-4 font-mono text-gray-300">
                            {instr.arg2 || "-"}
                          </td>
                          <td className="py-3 px-4 font-mono text-gray-300">
                            {instr.result || (instr.label ? instr.label : "-")}
                          </td>
                          <td className={`py-3 px-4 font-mono ${getInstructionColor(instr)}`}>
                            {highlightTokens(formatInstruction(instr))}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Code Listing
              </h2>
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="font-mono text-sm space-y-1">
                  {result.instructions.map((instr, idx) => (
                    <div key={idx} className="flex gap-3">
                      <span className="text-gray-500 w-8 text-right">
                        {idx + 1}
                      </span>
                      <span className={getInstructionColor(instr)}>
                        {highlightTokens(formatInstruction(instr))}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="text-sm text-gray-400 mb-1">Instructions</div>
                <div className="text-2xl font-bold text-blue-400">
                  {result.instructions.length}
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="text-sm text-gray-400 mb-1">Temp Variables</div>
                <div className="text-2xl font-bold text-green-400">
                  {result.temp_count}
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="text-sm text-gray-400 mb-1">Labels</div>
                <div className="text-2xl font-bold text-orange-400">
                  {result.label_count}
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Legend
              </h2>
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-pink-300 font-mono">#5</span>
                    <span className="text-gray-400">Literals</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-green-300 font-mono">temp1</span>
                    <span className="text-gray-400">Temporaries</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-blue-300 font-mono">x</span>
                    <span className="text-gray-400">Variables</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-orange-300 font-mono">L1</span>
                    <span className="text-gray-400">Labels</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-blue-400 font-mono">+, -, *, /</span>
                    <span className="text-gray-400">Arithmetic</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-yellow-400 font-mono">if_false</span>
                    <span className="text-gray-400">Control Flow</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
