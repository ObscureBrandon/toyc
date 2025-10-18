"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Play, Pause, SkipForward, SkipBack, RotateCcw } from "lucide-react";
import { apiClient, TraceResponse } from "@/lib/api";
import { useStepByStep } from "@/hooks/useStepByStep";
import { LexingPhase } from "./LexingPhase";
import { ParsingWithAST } from "./ParsingWithAST";
import { SemanticAnalysisPhase } from "./SemanticAnalysisPhase";

interface StepByStepVisualizerProps {
  initialCode?: string;
}

export function StepByStepVisualizer({
  initialCode = "x = 2.0 + 5 * 3 / 10.2\ny = (1.2 + 3) * 67",
}: StepByStepVisualizerProps) {
  const [sourceCode, setSourceCode] = useState(initialCode);
  const [traceData, setTraceData] = useState<TraceResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activePhase, setActivePhase] = useState<
    "lexing" | "parsing" | "semantic-analysis"
  >("lexing");

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
  } = useStepByStep(traceData?.steps || []);

  const handleTrace = async () => {
    if (!sourceCode.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.traceCode(sourceCode);
      setTraceData(response);

      if (!response.success && response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to trace code");
    } finally {
      setIsLoading(false);
    }
  };

  // Debounced auto-trace when source code changes
  useEffect(() => {
    const timer = setTimeout(() => {
      handleTrace();
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timer); // Cancel previous timer if user types again
  }, [sourceCode]);

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
          construction, and semantic analysis
        </p>
      </div>

      {/* Source Code Input */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
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
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-md p-4">
          <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
        </div>
      )}

      {traceData && (
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

            <div className="grid grid-cols-3 gap-4">
              {(["lexing", "parsing", "semantic-analysis"] as const).map(
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
                          : phase}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {phaseProgress[phase]} / {totalPhaseSteps[phase]} steps
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
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
              />
            )}

            {activePhase === "parsing" && (
              <ParsingWithAST
                visibleSteps={visibleSteps}
                currentStep={currentStepData}
              />
            )}

            {activePhase === "semantic-analysis" && (
              <SemanticAnalysisPhase
                visibleSteps={visibleSteps}
                currentStep={currentStepData}
                analyzedAst={traceData?.analyzed_ast}
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
