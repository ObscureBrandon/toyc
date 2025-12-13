'use client';

import { useState, useEffect, useCallback } from 'react';
import { AlertTriangle } from 'lucide-react';

interface UndefinedVariablesFormProps {
  variables: string[];
  mode: 'standard' | 'hybrid';
  onSubmit: (definitions: VariableDefinitions) => void;
}

export interface VariableDefinitions {
  types?: Record<string, 'int' | 'float'>;  // For standard mode
  values?: Record<string, number>;          // For hybrid mode
}

interface VariableInput {
  name: string;
  type: 'int' | 'float';
  value: string;
  isValid: boolean;
}

export function UndefinedVariablesForm({ variables, mode, onSubmit }: UndefinedVariablesFormProps) {
  const [inputs, setInputs] = useState<VariableInput[]>([]);

  // Initialize inputs when variables change
  useEffect(() => {
    setInputs(
      variables.map((name) => ({
        name,
        type: 'int' as const,
        value: '',
        isValid: mode === 'standard', // Standard mode is always valid (just a dropdown)
      }))
    );
  }, [variables, mode]);

  // Validate a value string
  const validateValue = useCallback((value: string): boolean => {
    if (value.trim() === '') return false;
    const num = parseFloat(value);
    return !isNaN(num) && isFinite(num);
  }, []);

  // Check if all inputs are valid
  const allValid = inputs.every((input) => input.isValid);

  // Handle type change (standard mode)
  const handleTypeChange = (index: number, type: 'int' | 'float') => {
    setInputs((prev) =>
      prev.map((input, i) =>
        i === index ? { ...input, type } : input
      )
    );
  };

  // Handle value change (hybrid mode)
  const handleValueChange = (index: number, value: string) => {
    const isValid = validateValue(value);
    setInputs((prev) =>
      prev.map((input, i) =>
        i === index ? { ...input, value, isValid } : input
      )
    );
  };

  // Handle form submission
  const handleSubmit = () => {
    if (!allValid) return;

    if (mode === 'standard') {
      const types: Record<string, 'int' | 'float'> = {};
      inputs.forEach((input) => {
        types[input.name] = input.type;
      });
      onSubmit({ types });
    } else {
      // Hybrid mode: send both values AND inferred types
      const values: Record<string, number> = {};
      const types: Record<string, 'int' | 'float'> = {};
      inputs.forEach((input) => {
        values[input.name] = parseFloat(input.value);
        // Determine type based on whether user typed a decimal point
        types[input.name] = input.value.includes('.') ? 'float' : 'int';
      });
      onSubmit({ values, types });
    }
  };

  if (variables.length === 0) {
    return null;
  }

  return (
    <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-4 mt-4">
      <div className="flex items-start gap-2 mb-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
        <div>
          <h3 className="font-semibold text-amber-800 dark:text-amber-200">
            Undefined Variables Detected
          </h3>
          <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
            {mode === 'standard'
              ? 'The following variables are used before being defined. Please specify their types:'
              : 'The following variables are used before being defined. Please provide their values:'}
          </p>
        </div>
      </div>

      <div className="space-y-3 mt-4">
        {inputs.map((input, index) => (
          <div key={input.name} className="flex items-center gap-3">
            <label className="w-20 font-mono text-sm font-medium text-gray-700 dark:text-gray-300">
              {input.name}:
            </label>

            {mode === 'standard' ? (
              <select
                value={input.type}
                onChange={(e) => handleTypeChange(index, e.target.value as 'int' | 'float')}
                className="px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="int">int</option>
                <option value="float">float</option>
              </select>
            ) : (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={input.value}
                  onChange={(e) => handleValueChange(index, e.target.value)}
                  placeholder="Enter value"
                  className={`px-3 py-1.5 rounded border text-sm w-32 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    input.value && !input.isValid
                      ? 'border-red-500 dark:border-red-400'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
                {input.value && !input.isValid && (
                  <span className="text-xs text-red-600 dark:text-red-400">
                    Invalid number
                  </span>
                )}
                {input.isValid && input.value && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {input.value.includes('.') ? 'float' : 'int'}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!allValid}
        className={`mt-4 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
          allValid
            ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
            : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
        }`}
      >
        Continue Compilation
      </button>
    </div>
  );
}
