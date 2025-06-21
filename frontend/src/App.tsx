import React, { useState, useEffect, useRef } from 'react';
import { InputSection } from './components/InputSection';
import { ActivityFeed } from './components/ActivityFeed';
import { ResultsSection } from './components/ResultsSection';
import { apiService, AgentRequest, Activity, Result } from './services/api';

interface AgentState {
  isRunning: boolean;
  mode: 'autonomous' | 'preview';
  activities: Activity[];
  results: Result[];
}

function App() {
  const [activeTab, setActiveTab] = useState<'activity' | 'results'>('activity');
  const [agentState, setAgentState] = useState<AgentState>({
    isRunning: false,
    mode: 'autonomous',
    activities: [],
    results: []
  });

  const [inputData, setInputData] = useState({
    topic: '',
    brandVoice: 'professional' as 'witty' | 'casual' | 'professional' | 'custom',
    customVoice: '',
    instructions: ''
  });

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState(false);
  const statusIntervalRef = useRef<number | null>(null);

  // Check API connection on mount
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    const isConnected = await apiService.checkApiHealth();
    setApiConnected(isConnected);
  };

  const handleRunAgent = async () => {
    if (agentState.isRunning) {
      // Stop agent
      if (sessionId) {
        try {
          await apiService.stopAgent(sessionId);
        } catch (error) {
          console.error('Error stopping agent:', error);
        }
      }
      setAgentState(prev => ({ ...prev, isRunning: false }));
      setSessionId(null);
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
      return;
    }

    // Validate input
    if (!inputData.topic || !inputData.instructions) {
      alert('Please fill in both topic and instructions');
      return;
    }

    // Start agent
    setAgentState(prev => ({ 
      ...prev, 
      isRunning: true, 
      activities: [], 
      results: [] 
    }));

    try {
      // Create brand instructions
      let brandInstructions = inputData.instructions;
      if (inputData.brandVoice === 'custom' && inputData.customVoice) {
        brandInstructions = `${inputData.customVoice}. ${inputData.instructions}`;
      }

      // Start agent via API
      const request: AgentRequest = {
        topic: inputData.topic,
        brand_instructions: brandInstructions,
        mode: agentState.mode
      };

      const response = await apiService.startAgent(request);
      setSessionId(response.session_id);

      // Start polling for status updates
      startStatusPolling(response.session_id);

    } catch (error) {
      console.error('Error starting agent:', error);
      setAgentState(prev => ({ ...prev, isRunning: false }));
      alert('Failed to start agent. Please check if the backend is running.');
    }
  };

  const startStatusPolling = (sessionId: string) => {
    // Poll every 2 seconds
    statusIntervalRef.current = setInterval(async () => {
      try {
        const status = await apiService.getAgentStatus(sessionId);
        
        setAgentState(prev => ({
          ...prev,
          isRunning: status.is_running,
          activities: status.activities,
          results: status.results
        }));

        // Stop polling if agent is done
        if (!status.is_running) {
          if (statusIntervalRef.current) {
            clearInterval(statusIntervalRef.current);
          }
          setSessionId(null);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        // Stop polling on error
        if (statusIntervalRef.current) {
          clearInterval(statusIntervalRef.current);
        }
        setAgentState(prev => ({ ...prev, isRunning: false }));
        setSessionId(null);
      }
    }, 2000);
  };

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      
      <div className="bg-white border-b border-gray-200">
       
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">PromoAgent</h1>
              <p className="text-sm text-gray-600 mt-1">Autonomous Reddit Marketing</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {apiConnected ? 'Backend Connected' : 'Backend Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex max-w-full mx-auto h-[calc(100vh-81px)]">
        {/* --- Left Sidebar: Configuration --- */}
        <div className="w-[400px] flex-shrink-0 bg-white border-r border-gray-200 p-6 overflow-y-auto">
          
          <InputSection
            inputData={inputData}
            setInputData={setInputData}
            agentState={agentState}
            setAgentState={setAgentState}
            onRunAgent={handleRunAgent}
          />
        </div>

        {/* --- Right Panel: Content Area --- */}
        <div className="flex-1 flex flex-col p-8 gap-8 overflow-hidden">
          <ActivityFeed activities={agentState.activities} isRunning={agentState.isRunning} />
          <ResultsSection results={agentState.results} />
        </div>
      </div>
    </div>
  );
}

export default App;