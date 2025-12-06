"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { Play, Pause, SkipForward, SkipBack, RotateCcw } from "lucide-react";
import { apiClient, TraceResponse } from "@/lib/api";
import { useStepByStep } from "@/hooks/useStepByStep";
import { UndefinedVariablesForm, VariableDefinitions } from "./UndefinedVariablesForm";
import { LexingPhase } from "./LexingPhase";
import { ParsingWithAST } from "./ParsingWithAST";
import { SemanticAnalysisPhase } from "./SemanticAnalysisPhase";
import { ICGPhase } from "./ICGPhase";
import { DirectExecutionPhase } from "./DirectExecutionPhase";

interface StepByStepVisualizerProps {
  initialCode?: string;
}

export function StepByStepVisualizer({
  initialCode = "x := y * (z - 2);",
}: StepByStepVisualizerProps) {
  const [sourceCode, setSourceCode] = useState(initialCode);
  const [traceData, setTraceData] = useState<TraceResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compilerMode, setCompilerMode] = useState<"standard" | "hybrid">("standard");
  const [activePhase, setActivePhase] = useState<
    "lexing" | "parsing" | "semantic-analysis" | "icg" | "execution"
  >("lexing");
  
  // Undefined variables state
  const [undefinedVariables, setUndefinedVariables] = useState<string[]>([]);
  const [showVariablePrompt, setShowVariablePrompt] = useState(false);

  // Use a ref to maintain stable steps reference
  const stepsRef = useRef<TraceResponse["steps"]>([]);
  
  // Only update stepsRef when steps array content actually changes
  const currentSteps = traceData?.steps || [];
  if (currentSteps.length !== stepsRef.current.length || 
      (currentSteps.length > 0 && currentSteps[0]?.step_id !== stepsRef.current[0]?.step_id)) {
    stepsRef.current = currentSteps;
  }
  const steps = stepsRef.current;

  const {
    controls,
    currentStepData,
    visibleSteps,
    play,
    pause,
    nextStep,
    previousStep,
    goToStep,
    setSpeed,
    reset,
  } = useStepByStep(steps);

  const handleTrace = useCallback(async (definitions?: VariableDefinitions) => {
    if (!sourceCode.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      // If no definitions provided, check for undefined variables first
      if (!definitions) {
        const checkResult = await apiClient.checkVariables(sourceCode);
        
        if (checkResult.success && checkResult.undefined_variables.length > 0) {
          // Found undefined variables - show the prompt
          setUndefinedVariables(checkResult.undefined_variables);
          setShowVariablePrompt(true);
          setIsLoading(false);
          return;
        }
      }

      // No undefined variables or definitions provided - proceed with trace
      setShowVariablePrompt(false);
      setUndefinedVariables([]);

      const response = await apiClient.traceCode(
        sourceCode,
        compilerMode,
        definitions?.types,
        definitions?.values,
      );
      setTraceData(response);

      if (!response.success && response.error) {
        const errorMsg = response.error_line !== undefined && response.error_column !== undefined
          ? `Error at line ${response.error_line}, column ${response.error_column}: ${response.error}`
          : response.error;
        setError(errorMsg);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to trace code");
    } finally {
      setIsLoading(false);
    }
  }, [sourceCode, compilerMode]);

  // Handle variable definitions from the form
  const handleVariableDefinitions = (definitions: VariableDefinitions) => {
    setShowVariablePrompt(false);
    handleTrace(definitions);
  };

  // Debounced auto-trace when source code or mode changes
  useEffect(() => {
    // Reset variable definitions when source or mode changes
    setShowVariablePrompt(false);
    setUndefinedVariables([]);
    
    const timer = setTimeout(() => {
      handleTrace();
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timer); // Cancel previous timer if user types again
  }, [handleTrace]);

  // Determine active phase based on current step
  useEffect(() => {
    if (currentStepData) {
      if (currentStepData.phase === "semantic-analysis") {
        setActivePhase("semantic-analysis");
      } else if (
        currentStepData.phase === "parsing" ||
        currentStepData.phase === "ast-building"
      ) {
        setActivePhase("parsing");
      } else {
        setActivePhase(
          currentStepData.phase as "lexing" | "parsing" | "semantic-analysis",
        );
      }
    }
  }, [currentStepData]);

  const phaseProgress = {
    lexing: visibleSteps.filter((s) => s.phase === "lexing").length,
    parsing: visibleSteps.filter(
      (s) => s.phase === "parsing" || s.phase === "ast-building",
    ).length,
    "semantic-analysis": visibleSteps.filter(
      (s) => s.phase === "semantic-analysis",
    ).length,
    icg: traceData && traceData.success && compilerMode === "standard" ? 1 : 0,
    execution: traceData && traceData.success && compilerMode === "hybrid" ? 1 : 0,
  };

  const totalPhaseSteps = {
    lexing: traceData?.steps.filter((s) => s.phase === "lexing").length || 0,
    parsing:
      traceData?.steps.filter(
        (s) => s.phase === "parsing" || s.phase === "ast-building",
      ).length || 0,
    "semantic-analysis":
      traceData?.steps.filter((s) => s.phase === "semantic-analysis").length ||
      0,
    icg: traceData && traceData.success && compilerMode === "standard" ? 1 : 0,
    execution: traceData && traceData.success && compilerMode === "hybrid" ? 1 : 0,
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Step-by-Step Compilation Visualizer
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Watch how your code is processed through lexing, parsing, AST
          construction, semantic analysis, code generation, and optimization
        </p>
      </div>

      {/* Source Code Input */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        {/* Mode Toggle Tabs */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Mode:</span>
          <div className="flex rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden">
            <button
              onClick={() => setCompilerMode("standard")}
              className={`px-4 py-1.5 text-sm font-medium transition-colors ${
                compilerMode === "standard"
                  ? "bg-blue-600 text-white"
                  : "bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
              }`}
            >
              Standard
            </button>
            <button
              onClick={() => setCompilerMode("hybrid")}
              className={`px-4 py-1.5 text-sm font-medium transition-colors ${
                compilerMode === "hybrid"
                  ? "bg-purple-600 text-white"
                  : "bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
              }`}
            >
              Hybrid
            </button>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
            {compilerMode === "standard" 
              ? "(Lexer → Parser → Semantic → ICG → Optimizer → Code Gen)"
              : "(Lexer → Parser → Semantic → Direct Execution)"}
          </span>
        </div>
        
        <label
          htmlFor="source-code"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Source Code
        </label>
        <textarea
          id="source-code"
          value={sourceCode}
          onChange={(e) => setSourceCode(e.target.value)}
          className="w-full h-20 p-3 border border-gray-300 dark:border-gray-600 rounded-md font-mono text-sm bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
          placeholder="Enter your code here..."
        />
        
        {/* Undefined Variables Form */}
        {showVariablePrompt && undefinedVariables.length > 0 && (
          <UndefinedVariablesForm
            variables={undefinedVariables}
            mode={compilerMode}
            onSubmit={handleVariableDefinitions}
          />
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
            Loading...
          </div>
        )}
        
        {/* Error display */}
        {error && !isLoading && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        )}
      </div>

      {traceData && !showVariablePrompt && (
        <>
          {/* Phase Progress Indicator */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                Compilation Progress
              </h3>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Step {controls.currentStep + 1} of {controls.totalSteps}
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4">
              {(compilerMode === "standard" 
                ? ["lexing", "parsing", "semantic-analysis", "icg"] as const
                : ["lexing", "parsing", "semantic-analysis", "execution"] as const
              ).map(
                (phase) => (
                  <div
                    key={phase}
                    className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                      activePhase === phase
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                        : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                    }`}
                    onClick={() => setActivePhase(phase)}
                  >
                    <div className="font-semibold text-sm text-gray-900 dark:text-gray-100 capitalize">
                      {phase === "parsing"
                        ? "Parsing & AST"
                        : phase === "semantic-analysis"
                          ? "Semantic Analysis"
                          : phase === "icg"
                            ? "Code Gen & Opt"
                            : phase === "execution"
                              ? "Direct Execution"
                              : phase}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {phaseProgress[phase]} / {totalPhaseSteps[phase]} steps
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          phase === "execution" ? "bg-purple-600" : "bg-blue-600"
                        }`}
                        style={{
                          width:
                            totalPhaseSteps[phase] > 0
                              ? `${(phaseProgress[phase] / totalPhaseSteps[phase]) * 100}%`
                              : "0%",
                        }}
                      />
                    </div>
                  </div>
                ),
              )}
            </div>
          </div>

          {/* Playback Controls */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={controls.isPlaying ? pause : play}
                  className="p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  title={controls.isPlaying ? "Pause" : "Play"}
                >
                  {controls.isPlaying ? (
                    <Pause size={20} />
                  ) : (
                    <Play size={20} />
                  )}
                </button>

                <button
                  onClick={previousStep}
                  disabled={!controls.canGoPrevious}
                  className="p-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Previous Step"
                >
                  <SkipBack size={20} />
                </button>

                <button
                  onClick={nextStep}
                  disabled={!controls.canGoNext}
                  className="p-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Next Step"
                >
                  <SkipForward size={20} />
                </button>

                <button
                  onClick={reset}
                  className="p-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                  title="Reset"
                >
                  <RotateCcw size={20} />
                </button>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-700 dark:text-gray-300">
                    Speed:
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="3"
                    step="0.1"
                    value={controls.speed}
                    onChange={(e) => setSpeed(parseFloat(e.target.value))}
                    className="w-20"
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400 w-8">
                    {controls.speed}x
                  </span>
                </div>
              </div>
            </div>

            {/* Progress Timeline */}
            <div className="mt-4">
              <input
                type="range"
                min="0"
                max={controls.totalSteps - 1}
                value={controls.currentStep}
                onChange={(e) => goToStep(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          </div>

          {/* Phase Content */}
          <motion.div
            key={activePhase}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {activePhase === "lexing" && (
              <LexingPhase
                sourceCode={sourceCode}
                visibleSteps={visibleSteps}
                currentStep={currentStepData}
                compilerMode={compilerMode}
              />
            )}

            {activePhase === "parsing" && (
              <ParsingWithAST
                visibleSteps={visibleSteps}
                currentStep={currentStepData}
                identifierMapping={traceData?.identifier_mapping}
                compilerMode={compilerMode}
              />
            )}

            {activePhase === "semantic-analysis" && (
              <SemanticAnalysisPhase
                visibleSteps={visibleSteps}
                currentStep={currentStepData}
                analyzedAst={traceData?.analyzed_ast}
                identifierMapping={traceData?.identifier_mapping}
                compilerMode={compilerMode}
              />
            )}

            {activePhase === "icg" && compilerMode === "standard" && (
              <ICGPhase sourceCode={sourceCode} />
            )}

            {activePhase === "execution" && compilerMode === "hybrid" && (
              <DirectExecutionPhase
                executedAst={traceData?.executed_ast}
                variables={traceData?.variables}
                output={traceData?.output}
                identifierMapping={traceData?.identifier_mapping}
                sourceCode={sourceCode}
              />
            )}
          </motion.div>

          {/* Current Step Info */}
          {currentStepData && (
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
              <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
                Current Step
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Phase:
                  </span>
                  <span className="font-mono capitalize">
                    {currentStepData.phase}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Step ID:
                  </span>
                  <span className="font-mono">{currentStepData.step_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Description:
                  </span>
                  <span className="text-right flex-1 ml-2">
                    {currentStepData.description}
                  </span>
                </div>
                {currentStepData.position !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">
                      Position:
                    </span>
                    <span className="font-mono">
                      {currentStepData.position}
                    </span>
                  </div>
                )}
                
                {/* Error Details */}
                {currentStepData.state?.error_type && currentStepData.state?.message && (
                  <div className="mt-4 p-3 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-md">
                    <div className="flex items-start gap-2">
                      <span className="text-red-600 dark:text-red-400 text-lg">⚠️</span>
                      <div className="flex-1">
                        <div className="font-semibold text-red-800 dark:text-red-200 mb-1">
                          {currentStepData.state.error_type as string}
                        </div>
                        <div className="text-red-700 dark:text-red-300 text-sm">
                          {currentStepData.state.message as string}
                        </div>
                        
                        {/* Show error node details if available */}
                        {currentStepData.state.ast_node && 
                         typeof currentStepData.state.ast_node === 'object' && 
                         'type' in currentStepData.state.ast_node && 
                         currentStepData.state.ast_node.type === 'Error' && (
                          <div className="mt-3 space-y-2 text-xs">
                            {'position' in currentStepData.state.ast_node && 
                             typeof currentStepData.state.ast_node.position === 'object' &&
                             currentStepData.state.ast_node.position !== null &&
                             'line' in currentStepData.state.ast_node.position && 
                             'col' in currentStepData.state.ast_node.position && (
                              <div>
                                <span className="font-semibold">Location: </span>
                                <span className="font-mono">
                                  line {currentStepData.state.ast_node.position.line as number}, column {currentStepData.state.ast_node.position.col as number}
                                </span>
                              </div>
                            )}
                            {'expected' in currentStepData.state.ast_node && 
                             Array.isArray(currentStepData.state.ast_node.expected) && 
                             currentStepData.state.ast_node.expected.length > 0 && (
                              <div>
                                <span className="font-semibold">Expected: </span>
                                <span className="font-mono">
                                  {(currentStepData.state.ast_node.expected as string[]).join(', ')}
                                </span>
                              </div>
                            )}
                            {'found' in currentStepData.state.ast_node && (
                              <div>
                                <span className="font-semibold">Found: </span>
                                <span className="font-mono">
                                  {currentStepData.state.ast_node.found as string}
                                </span>
                              </div>
                            )}
                            {'context' in currentStepData.state.ast_node && 
                             currentStepData.state.ast_node.context && (
                              <div>
                                <span className="font-semibold">Context: </span>
                                <pre className="font-mono mt-1 p-2 bg-red-100 dark:bg-red-900 rounded overflow-x-auto">
                                  {currentStepData.state.ast_node.context as string}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Grammar Rules - Full width at bottom */}
          {/* {traceData && ( */}
          {/*   <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border"> */}
          {/*     <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100"> */}
          {/*       Grammar Rules */}
          {/*     </h3> */}
          {/*     <div className="text-sm space-y-1 font-mono text-gray-700 dark:text-gray-300"> */}
          {/*       <div>program → statement*</div> */}
          {/*       <div>statement → assignment | expression</div> */}
          {/*       <div>assignment → IDENTIFIER '=' expression ';'</div> */}
          {/*       <div>expression → term (('+' | '-') term)*</div> */}
          {/*       <div>term → factor (('*' | '/') factor)*</div> */}
          {/*       <div>factor → primary | '(' expression ')'</div> */}
          {/*       <div>primary → NUMBER | FLOAT | IDENTIFIER</div> */}
          {/*     </div> */}
          {/*   </div> */}
          {/* )} */}
        </>
      )}
    </div>
  );
}
