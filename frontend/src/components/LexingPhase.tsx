'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { TraceStep } from '@/lib/api';

interface LexingPhaseProps {
  sourceCode: string;
  visibleSteps: TraceStep[];
  currentStep: TraceStep | null;
}

interface TokenPreview {
  type: string;
  literal: string;
  position: number;
  isComplete: boolean;
  isBuilding: boolean;
}

export function LexingPhase({ sourceCode, visibleSteps, currentStep }: LexingPhaseProps) {
  // Filter to lexing phase steps
  const lexingSteps = visibleSteps.filter(step => step.phase === 'lexing');
  
  // Get current position in source code
  const currentPosition = currentStep?.position ?? 0;
  
  // Extract tokens from visible steps
  const completedTokens: TokenPreview[] = [];
  let currentToken: TokenPreview | null = null;
  let tokenStartPosition: number = 0;
  
  for (const step of lexingSteps) {
    if (step.state.action === 'token_created') {
      completedTokens.push({
        type: step.state.token_type,
        literal: step.state.literal,
        position: tokenStartPosition, // Use start position, not current position
        isComplete: true,
        isBuilding: false,
      });
      currentToken = null; // Clear current when token is completed
    } else if (step.state.action === 'identify_token') {
      // Start of a new token - record the start position
      tokenStartPosition = step.position || 0;
      currentToken = {
        type: step.state.token_type || 'unknown',
        literal: step.state.current_char || '',
        position: tokenStartPosition,
        isComplete: false,
        isBuilding: false,
      };
    } else if (step.state.action === 'build_token' && currentToken) {
      // Update current token with incremental lexeme
      currentToken = {
        ...currentToken,
        literal: step.state.current_lexeme || currentToken.literal,
        isBuilding: true,
      };
    }
  }

  const renderSourceCode = () => {
    const chars = sourceCode.split('');
    
    return (
      <div className="font-mono text-sm leading-relaxed">
        {chars.map((char, index) => {
          const isCurrentChar = index === currentPosition && currentStep?.phase === 'lexing';
          
          // Check if this character is part of a completed token
          const completedTokenAtIndex = completedTokens.find(
            token => index >= token.position && index < token.position + token.literal.length
          );
          
          // Check if this character is part of the current token being built
          const isInCurrentToken = currentToken && 
            index >= currentToken.position && 
            index < currentToken.position + currentToken.literal.length;
          
          let className = 'relative ';
          
          if (isCurrentChar) {
            className += 'bg-yellow-400 text-black animate-pulse ';
          } else if (completedTokenAtIndex) {
            // Use token-specific color for completed tokens
            className += getTokenBackgroundColor(completedTokenAtIndex.type);
          } else if (isInCurrentToken) {
            // Use light color for token being built
            className += getTokenBuildingColor(currentToken.type);
          }
          
          return (
            <motion.span
              key={index}
              className={className}
              initial={{ opacity: 0.5 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              {char === ' ' ? '·' : char === '\n' ? '↵' : char}
            </motion.span>
          );
        })}
      </div>
    );
  };

  const getTokenTypeName = (type: string) => {
    return type;
  };

  const getTokenTypeColor = (type: string) => {
    const colorMap: Record<string, string> = {
      'NUMBER': 'bg-purple-500 text-white',
      'FLOAT': 'bg-purple-500 text-white',
      'IDENTIFIER': 'bg-blue-500 text-white',
      '+': 'bg-orange-500 text-white',
      '-': 'bg-orange-500 text-white',
      '*': 'bg-orange-500 text-white',
      '/': 'bg-orange-500 text-white',
      '=': 'bg-orange-500 text-white',
      '(': 'bg-orange-500 text-white',
      ')': 'bg-orange-500 text-white',
      ';': 'bg-orange-500 text-white',
      'EOF': 'bg-red-500 text-white',
      'ILLEGAL': 'bg-red-600 text-white',
      // Legacy support for descriptive names
      'PLUS': 'bg-orange-500 text-white',
      'MINUS': 'bg-orange-500 text-white',
      'ASTERISK': 'bg-orange-500 text-white',
      'SLASH': 'bg-orange-500 text-white',
      'EQUAL': 'bg-orange-500 text-white',
      'LPAREN': 'bg-orange-500 text-white',
      'RPAREN': 'bg-orange-500 text-white',
      'SEMICOLON': 'bg-orange-500 text-white',
    };
    return colorMap[type] || 'bg-gray-500 text-white';
  };

  const getTokenBackgroundColor = (type: string) => {
    const colorMap: Record<string, string> = {
      'NUMBER': 'bg-purple-500 text-white ',
      'FLOAT': 'bg-purple-500 text-white ',
      'IDENTIFIER': 'bg-blue-500 text-white ',
      '+': 'bg-orange-500 text-white ',
      '-': 'bg-orange-500 text-white ',
      '*': 'bg-orange-500 text-white ',
      '/': 'bg-orange-500 text-white ',
      '=': 'bg-orange-500 text-white ',
      '(': 'bg-orange-500 text-white ',
      ')': 'bg-orange-500 text-white ',
      ';': 'bg-orange-500 text-white ',
      'EOF': 'bg-red-500 text-white ',
      'ILLEGAL': 'bg-red-600 text-white ',
      // Legacy support for descriptive names
      'PLUS': 'bg-orange-500 text-white ',
      'MINUS': 'bg-orange-500 text-white ',
      'ASTERISK': 'bg-orange-500 text-white ',
      'SLASH': 'bg-orange-500 text-white ',
      'EQUAL': 'bg-orange-500 text-white ',
      'LPAREN': 'bg-orange-500 text-white ',
      'RPAREN': 'bg-orange-500 text-white ',
      'SEMICOLON': 'bg-orange-500 text-white ',
    };
    return colorMap[type] || 'bg-gray-500 text-white ';
  };

  const getTokenBuildingColor = (type: string) => {
    const colorMap: Record<string, string> = {
      'NUMBER': 'bg-purple-300 text-black ',
      'FLOAT': 'bg-purple-300 text-black ',
      'IDENTIFIER': 'bg-blue-300 text-black ',
      '+': 'bg-orange-300 text-black ',
      '-': 'bg-orange-300 text-black ',
      '*': 'bg-orange-300 text-black ',
      '/': 'bg-orange-300 text-black ',
      '=': 'bg-orange-300 text-black ',
      '(': 'bg-orange-300 text-black ',
      ')': 'bg-orange-300 text-black ',
      ';': 'bg-orange-300 text-black ',
      'EOF': 'bg-red-300 text-black ',
      'ILLEGAL': 'bg-red-300 text-black ',
      // Legacy support for descriptive names
      'PLUS': 'bg-orange-300 text-black ',
      'MINUS': 'bg-orange-300 text-black ',
      'ASTERISK': 'bg-orange-300 text-black ',
      'SLASH': 'bg-orange-300 text-black ',
      'EQUAL': 'bg-orange-300 text-black ',
      'LPAREN': 'bg-orange-300 text-black ',
      'RPAREN': 'bg-orange-300 text-black ',
      'SEMICOLON': 'bg-orange-300 text-black ',
    };
    return colorMap[type] || 'bg-gray-300 text-black ';
  };

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Source Code
        </h3>
        <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded border-2 border-dashed">
          {renderSourceCode()}
        </div>
        {currentStep && (
          <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Current Position: {currentPosition} | {currentStep.description}
          </div>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Token Stream
        </h3>
        <div className="flex flex-wrap gap-2 min-h-[100px] items-start">
          <AnimatePresence>
            {completedTokens.map((token, index) => (
              <motion.div
                key={`completed-${index}`}
                initial={{ opacity: 0, scale: 0.8, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={`min-w-[4rem] min-h-[4rem] px-2 py-1 rounded-lg flex flex-col items-center justify-center text-xs font-semibold shadow-md ${getTokenTypeColor(token.type)}`}
              >
                <div className="text-xs font-bold mb-1 text-center">{getTokenTypeName(token.type)}</div>
                <div className="text-xs font-mono text-center break-all">'{token.literal}'</div>
              </motion.div>
            ))}
            
            {currentToken && (
              <motion.div
                key="current-token"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2 }}
                className={`min-w-[4rem] min-h-[4rem] px-2 py-1 rounded-lg flex flex-col items-center justify-center text-xs font-semibold shadow-md border-2 border-dashed ${getTokenTypeColor(currentToken.type)} ${currentToken.isBuilding ? 'animate-pulse' : ''}`}
              >
                <div className="text-xs font-bold mb-1 text-center">{getTokenTypeName(currentToken.type)}</div>
                <div className="text-xs font-mono text-center break-all">'{currentToken.literal}'</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="font-semibold mb-2 text-gray-900 dark:text-gray-100">
          Lexer State
        </h3>
        {currentStep && currentStep.phase === 'lexing' ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Position:</span>
              <span className="font-mono">{currentStep.position}</span>
            </div>
            {currentStep.state.current_char && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Current Char:</span>
                <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">
                  '{currentStep.state.current_char}'
                </span>
              </div>
            )}
            {currentStep.state.current_lexeme && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Current Lexeme:</span>
                <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">
                  '{currentStep.state.current_lexeme}'
                </span>
              </div>
            )}
            {currentStep.state.token_type && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Token Type:</span>
                <span className={`px-2 py-1 rounded text-xs ${getTokenTypeColor(currentStep.state.token_type)}`}>
                  {currentStep.state.token_type}
                </span>
              </div>
            )}
            {currentStep.state.action && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Action:</span>
                <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">
                  {currentStep.state.action}
                </span>
              </div>
            )}
          </div>
        ) : (
          <div className="text-gray-500 dark:text-gray-400 text-sm">
            Waiting for lexing step...
          </div>
        )}
      </div>
    </div>
  );
}