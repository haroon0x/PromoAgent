/**
 * API service for communicating with PromoAgent backend
 */

const API_BASE_URL = 'http://localhost:8000';

export interface AgentRequest {
  topic: string;
  brand_instructions: string;
  mode: string;
}

export interface AgentResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface Activity {
  id: string;
  timestamp: string;
  type: string;
  message: string;
  status: string;
}

export interface Result {
  id: string;
  thread_title: string;
  submission_url: string;
  post_url: string;
  generated_reply: string;
  posted: boolean;
  timestamp: string;
}

export interface AgentStatus {
  session_id: string;
  is_running: boolean;
  activities: Activity[];
  results: Result[];
}

class ApiService {
  async startAgent(request: AgentRequest): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/api/agent/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to start agent: ${response.statusText}`);
    }

    return response.json();
  }

  async getAgentStatus(sessionId: string): Promise<AgentStatus> {
    const response = await fetch(`${API_BASE_URL}/api/agent/${sessionId}/status`);

    if (!response.ok) {
      throw new Error(`Failed to get agent status: ${response.statusText}`);
    }

    return response.json();
  }

  async stopAgent(sessionId: string): Promise<AgentResponse> {
    const response = await fetch(`${API_BASE_URL}/api/agent/${sessionId}/stop`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to stop agent: ${response.statusText}`);
    }

    return response.json();
  }

  async checkApiHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService(); 