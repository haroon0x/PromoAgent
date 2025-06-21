import React from 'react';
import { Play, Square } from 'lucide-react';

interface InputSectionProps {
  inputData: {
    topic: string;
    brandVoice: 'witty' | 'casual' | 'professional' | 'custom';
    customVoice: string;
    instructions: string;
  };
  setInputData: React.Dispatch<React.SetStateAction<any>>;
  agentState: {
    isRunning: boolean;
    mode: 'autonomous' | 'preview';
  };
  setAgentState: React.Dispatch<React.SetStateAction<any>>;
  onRunAgent: () => void;
}

export function InputSection({ 
  inputData, 
  setInputData, 
  agentState, 
  setAgentState, 
  onRunAgent 
}: InputSectionProps) {
  const brandVoiceOptions = [
    { value: 'witty', label: 'Witty' },
    { value: 'casual', label: 'Casual' },
    { value: 'professional', label: 'Professional' },
    { value: 'custom', label: 'Custom' }
  ];

  return (
    <div className="flex flex-col h-full">
      
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Configuration</h2>
      
      <div className="space-y-6 flex-1">
        {/* Topic/Query */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Topic
          </label>
          <input
            type="text"
            value={inputData.topic}
            onChange={(e) => setInputData((prev: typeof inputData) => ({ ...prev, topic: e.target.value }))}
            placeholder="best AI tools for founders"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Brand Voice */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Brand Voice
          </label>
          <div className="grid grid-cols-2 gap-2">
            {brandVoiceOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setInputData((prev: typeof inputData) => ({ 
                  ...prev, 
                  brandVoice: option.value as typeof inputData.brandVoice 
                }))}
                className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                  inputData.brandVoice === option.value
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
          
          {inputData.brandVoice === 'custom' && (
            <textarea
              value={inputData.customVoice}
              onChange={(e) => setInputData((prev: typeof inputData) => ({ ...prev, customVoice: e.target.value }))}
              placeholder="Describe your brand voice..."
              className="w-full mt-3 px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none h-20"
            />
          )}
        </div>

        {/* Instructions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Instructions
          </label>
          <textarea
            value={inputData.instructions}
            onChange={(e) => setInputData((prev: typeof inputData) => ({ ...prev, instructions: e.target.value }))}
            placeholder="Try our new product X! Sign up at example.com"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none h-20"
          />
        </div>

        {/* Mode Toggle */}
        <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-md">
          <div>
            <div className="text-sm font-medium text-gray-900">Mode</div>
            <div className="text-xs text-gray-600">
              {agentState.mode === 'autonomous' ? 'Auto-post replies' : 'Preview only'}
            </div>
          </div>
          <button
            onClick={() => setAgentState((prev: typeof agentState) => ({ 
              ...prev, 
              mode: prev.mode === 'autonomous' ? 'preview' : 'autonomous' 
            }))}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
              agentState.mode === 'autonomous' ? 'bg-blue-600' : 'bg-gray-400'
            }`}
          >
            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
              agentState.mode === 'autonomous' ? 'translate-x-5' : 'translate-x-1'
            }`} />
          </button>
        </div>
      </div><div className="mb-2 text-xs text-gray-600 text-center font-medium">
        Powered by Alchemyst AI (alchemyst-ai/alchemyst-c1)
      </div>

      {/* Run Button */}
      <div className="mt-6">
        <button
          onClick={onRunAgent}
          disabled={!inputData.topic || !inputData.instructions}
          className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-md font-medium transition-colors ${
            agentState.isRunning
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed'
          }`}
        >
          {agentState.isRunning ? (
            <>
              <Square className="h-4 w-4" />
              <span>Stop</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              <span>Run Agent</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}