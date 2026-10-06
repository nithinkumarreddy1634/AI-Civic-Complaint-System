import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import SeverityBadge from './SeverityBadge';
import PriorityBadge from './PriorityBadge';

const AIResultCard = ({ result }) => {
  if (!result) return null;

  return (
    <div className="bg-white rounded-xl border border-blue-100 shadow-sm overflow-hidden">
      <div className="bg-blue-50 px-4 py-3 border-b border-blue-100 flex items-center justify-between">
        <div className="flex items-center gap-2 text-blue-800 font-semibold">
          <ShieldCheck size={18} />
          <span>AI Verification Complete</span>
        </div>
        {result.verified ? (
          <span className="flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded-full">
            <CheckCircle2 size={12} /> Confirmed
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs font-medium text-yellow-700 bg-yellow-100 px-2 py-1 rounded-full">
            <AlertTriangle size={12} /> Needs Manual Check
          </span>
        )}
      </div>

      <div className="p-4 space-y-4">
        <div>
          <div className="flex justify-between items-end mb-1">
            <span className="text-sm font-medium text-gray-600">Detected Object</span>
            <span className="text-sm font-bold text-gray-900">{result.label}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full" 
              style={{ width: `${(result.confidence * 100).toFixed(0)}%` }}
            ></div>
          </div>
          <p className="text-xs text-right text-gray-500 mt-1">
            {(result.confidence * 100).toFixed(1)}% Confidence
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-100">
          <div>
            <span className="block text-xs text-gray-500 mb-1">Assessed Severity</span>
            <SeverityBadge level={result.severity} score={result.severityScore} />
          </div>
          <div>
            <span className="block text-xs text-gray-500 mb-1">Calculated Priority</span>
            <PriorityBadge level={result.priority} score={result.priorityScore} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIResultCard;
