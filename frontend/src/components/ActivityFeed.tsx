import React from 'react';
import { Terminal } from 'lucide-react';

interface ActivityItem {
  id: string;
  timestamp: string;
  type: string;
  message: string;
  status: string;
}

interface ActivityFeedProps {
  activities: ActivityItem[];
  isRunning: boolean;
}

export function ActivityFeed({ activities, isRunning }: ActivityFeedProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'error': return 'text-red-600';
      default: return 'text-blue-600';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="flex flex-col h-2/5 min-h-[200px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-4">
        <div className="flex items-center space-x-3">
          <Terminal className="h-6 w-6 text-gray-500" />
          <h2 className="text-xl font-semibold text-gray-900">Activity Feed</h2>
        </div>
        {isRunning && (
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-600 font-medium">Running</span>
          </div>
        )}
      </div>

      {/* Terminal Content */}
      <div className="flex-1 bg-gray-900 rounded-md p-4 font-mono text-sm overflow-y-auto">
        {activities.length === 0 && !isRunning ? (
          <div className="text-gray-500 text-center flex flex-col items-center justify-center h-full">
            <Terminal className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Waiting for agent to start...</p>
            <p className="text-xs text-gray-600 mt-2">Your agent's progress will appear here.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {activities.map((activity, index) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <span className="text-gray-500 text-xs mt-1 w-20 flex-shrink-0">
                  {formatTimestamp(activity.timestamp)}
                </span>
                <div className="flex-1">
                  <div className={`${getStatusColor(activity.status)} leading-relaxed`}>
                    {activity.message}
                  </div>
                  {activity.status === 'in-progress' && (
                    <div className="mt-1">
                      <div className="flex space-x-1">
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isRunning && activities.length > 0 && (
              <div className="flex items-center space-x-2 text-gray-500">
                <span className="text-xs">
                  {new Date().toLocaleTimeString()}
                </span>
                <span className="text-blue-400">█</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}