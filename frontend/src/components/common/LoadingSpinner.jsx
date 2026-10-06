import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ fullScreen = false }) => {
  const content = (
    <div className="flex flex-col items-center justify-center p-4">
      <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
      <span className="mt-2 text-sm text-gray-500">Loading...</span>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
};

export default LoadingSpinner;
