"use client";

import { useState } from "react";
import { apiClient, type LexerResponse } from "@/lib/api";

export default function LexerVisualizer() {
  const placeholderCode = `x = 5 + 3.14 * (y - 2)
result = x / 2`;

  const [sourceCode, setSourceCode] = useState(placeholderCode);
  const [result, setResult] = useState<LexerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLex = async () => {
    const codeToTokenize = sourceCode.trim() || placeholderCode;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.lexCode(codeToTokenize);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to tokenize code");
    } finally {
      setLoading(false);
    }
  };

  const getTokenColor = (type: string): string => {
    const colors: Record<string, string> = {
      NUMBER: "bg-blue-900/20 text-blue-300 border border-blue-700/30",
      FLOAT: "bg-blue-900/20 text-blue-300 border border-blue-700/30",
      IDENTIFIER: "bg-green-900/20 text-green-300 border border-green-700/30",
      PLUS: "bg-purple-900/20 text-purple-300 border border-purple-700/30",
      MINUS: "bg-purple-900/20 text-purple-300 border border-purple-700/30",
      ASTERISK: "bg-purple-900/20 text-purple-300 border border-purple-700/30",
      SLASH: "bg-purple-900/20 text-purple-300 border border-purple-700/30",
      PERCENT: "bg-purple-900/20 text-purple-300 border border-purple-700/30",
      ASSIGN: "bg-yellow-900/20 text-yellow-300 border border-yellow-700/30",
      LPAREN: "bg-green-900/20 text-green-300 border border-green-700/30",
      RPAREN: "bg-green-900/20 text-green-300 border border-green-700/30",
      SEMICOLON: "bg-green-900/20 text-green-300 border border-green-700/30",
      LT: "bg-cyan-900/20 text-cyan-300 border border-cyan-700/30",
      GT: "bg-cyan-900/20 text-cyan-300 border border-cyan-700/30",
      EQ: "bg-cyan-900/20 text-cyan-300 border border-cyan-700/30",
      NEQ: "bg-cyan-900/20 text-cyan-300 border border-cyan-700/30",
      LT_EQ: "bg-cyan-900/20 text-cyan-300 border border-cyan-700/30",
      GT_EQ: "bg-cyan-900/20 text-cyan-300 border border-cyan-700/30",
      AND: "bg-pink-900/20 text-pink-300 border border-pink-700/30",
      OR: "bg-pink-900/20 text-pink-300 border border-pink-700/30",
      IF: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      ELSE: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      END: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      REPEAT: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      UNTIL: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      READ: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      WRITE: "bg-indigo-900/20 text-indigo-300 border border-indigo-700/30",
      ILLEGAL: "bg-red-900/20 text-red-300 border border-red-700/30",
      EOF: "bg-gray-800/30 text-gray-500 border border-gray-600/20",
    };
    return (
      colors[type] || "bg-gray-800/50 text-gray-300 border border-gray-600/30"
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-4xl font-bold mb-8 text-center text-white">
          ToyC Lexer Visualizer
        </h1>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2 text-gray-300">
            Source Code:
          </label>
          <textarea
            value={sourceCode}
            onChange={(e) => setSourceCode(e.target.value)}
            className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg font-mono text-sm text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={6}
            placeholder={placeholderCode}
          />
        </div>

        <div className="mb-6 flex gap-4">
          <button
            onClick={handleLex}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {loading ? "Tokenizing..." : "Tokenize"}
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

        {result && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Token Visualization
              </h2>
              <div className="flex flex-wrap gap-3">
                {result.tokens.map(
                  (token, idx) =>
                    token.type !== "EOF" && (
                      <div
                        key={idx}
                        className={`px-4 py-3 rounded-lg shadow-sm ${getTokenColor(token.type)}`}
                      >
                        <div className="text-xs font-bold uppercase tracking-wide">
                          {token.type}
                        </div>
                        <div className="font-mono text-sm mt-1">
                          {token.literal || "<empty>"}
                        </div>
                      </div>
                    ),
                )}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Identifier Mapping
              </h2>
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="flex flex-wrap gap-3">
                  {Object.entries(result.identifier_mapping).map(
                    ([original, normalized]) => (
                      <div
                        key={original}
                        className="bg-blue-900/30 border border-blue-600/50 rounded-lg px-4 py-2 flex items-center gap-2"
                      >
                        <span className="font-mono text-sm text-gray-200 font-medium">
                          {original}
                        </span>
                        <span className="text-gray-400">→</span>
                        <span className="font-mono text-sm text-blue-400 font-semibold">
                          {normalized}
                        </span>
                      </div>
                    ),
                  )}
                  {Object.keys(result.identifier_mapping).length === 0 && (
                    <div className="text-gray-400 text-sm">
                      No identifiers found in source code
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Normalized Representation
                <span className="ml-2 text-xs text-gray-400 font-normal">
                  (identifiers normalized to id1, id2, id3...)
                </span>
              </h2>
              <div className="bg-gray-800/50 rounded-lg p-4 shadow-sm border border-gray-700/30">
                <div className="font-mono text-sm text-gray-200 whitespace-pre-wrap break-words">
                  {result.normalized_code}
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-400">
                Identifiers are replaced with id1, id2, id3... in order of first appearance
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4 text-gray-200">
                Token Stream
              </h2>
              <div className="bg-gray-800/50 rounded-lg overflow-hidden shadow-sm border border-gray-700/30">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-700/50">
                      <tr>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Position
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Line
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Column
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Type
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Literal
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.tokens.map((token, idx) => (
                        <tr
                          key={idx}
                          className="border-b border-gray-700/30 hover:bg-gray-700/20"
                        >
                          <td className="py-3 px-4 font-mono text-gray-400">
                            {token.position}
                          </td>
                          <td className="py-3 px-4 font-mono text-gray-400">
                            {token.line}
                          </td>
                          <td className="py-3 px-4 font-mono text-gray-400">
                            {token.column}
                          </td>
                          <td className="py-3 px-4 font-mono font-medium text-gray-200">
                            {token.type}
                          </td>
                          <td className="py-3 px-4 font-mono text-gray-200">
                            {token.literal || "<EOF>"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
