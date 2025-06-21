import React from 'react';
import { FileText, ExternalLink, CheckCircle, Clock } from 'lucide-react';
import { Result } from '../services/api';

interface ResultsSectionProps {
  results: Result[];
}

export function ResultsSection({ results }: ResultsSectionProps) {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="flex flex-col h-3/5">
      <div className="flex items-center justify-between pb-4">
        <div className="flex items-center space-x-3">
          <FileText className="h-6 w-6 text-gray-500" />
          <h2 className="text-xl font-semibold text-gray-900">Results</h2>
        </div>
        {results.length > 0 && (
          <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
            {results.length} results
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto -mr-6 pr-6">
        {results.length === 0 ? (
          <div className="text-center flex flex-col items-center justify-center h-full">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500">No results yet</p>
            <p className="text-sm text-gray-400 mt-1">Generated replies will appear here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {results.map((result) => (
              <div key={result.id} className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
                {/* Status and Title */}
                <div className="flex items-start justify-between">
                  <a
                    href={result.submission_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-gray-900 text-sm leading-tight pr-2 hover:text-blue-600 transition-colors"
                  >
                    {result.thread_title}
                  </a>
                  <div className="flex-shrink-0">
                    {result.posted ? (
                      <div className="flex items-center space-x-1 bg-green-50 text-green-700 px-2 py-1 rounded-full">
                        <CheckCircle className="h-3 w-3" />
                        <span className="text-xs font-medium">Posted</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1 bg-yellow-50 text-yellow-700 px-2 py-1 rounded-full">
                        <Clock className="h-3 w-3" />
                        <span className="text-xs font-medium">Preview</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Generated Reply */}
                <div className="bg-gray-50 rounded-md p-3">
                  <p className="text-sm text-gray-700 leading-relaxed">{result.generated_reply}</p>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{formatTimestamp(result.timestamp)}</span>
                  {result.post_url && (
                    <a
                      href={result.post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 font-medium text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <span>View Comment</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}