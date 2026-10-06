import React from 'react';
import { getSeverityColor } from '../../utils/helpers';
import { SEVERITY_LEVELS } from '../../utils/constants';

const SeverityBadge = ({ level, score }) => {
  if (!level) return null;

  const upper = level.toUpperCase();
  const colorClass = getSeverityColor(upper);
  const label = SEVERITY_LEVELS[upper]?.label || level;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colorClass}`}>
      {label}
      {score !== undefined && score !== null && (
        <span className="opacity-75 border-l border-current pl-1.5 ml-0.5 font-mono">
          {typeof score === 'number' ? score.toFixed(0) : score}
        </span>
      )}
    </span>
  );
};

export default SeverityBadge;
