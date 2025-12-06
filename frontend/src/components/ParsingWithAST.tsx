"use client";

import React from "react";
import { TraceStep } from "@/lib/api";
import { ParsingPhase } from "./ParsingPhase";
import { AnimatedAST } from "./AnimatedAST";
import { ASTNodeLog } from "./ASTNodeLog";

interface ParsingWithASTProps {
  visibleSteps: TraceStep[];
  currentStep: TraceStep | null;
  identifierMapping?: Record<string, string>;
}

export function ParsingWithAST({
  visibleSteps,
  currentStep,
  identifierMapping,
}: ParsingWithASTProps) {
  return (
    <div className="space-y-6">
      {/* Top: AST Graph - Full width */}
      <div className="w-full">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          AST Construction
        </h3>
        <AnimatedAST visibleSteps={visibleSteps} currentStep={currentStep} identifierMapping={identifierMapping} />
      </div>

      {/* Bottom: Parser trace and AST log side by side */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Parser trace and state */}
        <div className="flex-1 flex flex-col">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Parser Trace
          </h3>
          <div className="flex-grow">
            <ParsingPhase visibleSteps={visibleSteps} currentStep={currentStep} />
          </div>
        </div>

        {/* Right: AST Node Creation Log */}
        <div className="flex-1 flex flex-col">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            AST Node Log
          </h3>
          <div className="flex-grow">
            <ASTNodeLog visibleSteps={visibleSteps} currentStep={currentStep} />
          </div>
        </div>
      </div>
    </div>
  );
}

