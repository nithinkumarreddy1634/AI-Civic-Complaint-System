import React from 'react';
import { getPriorityColor } from '../../utils/helpers';
import { PRIORITY_LEVELS } from '../../utils/constants';

const PriorityBadge = ({ level, score }) => {
  let rawLevel = level;
  let rawScore = score;

  if (typeof rawLevel === 'object' && rawLevel !== null) {
    rawScore = rawScore ?? rawLevel.score ?? rawLevel.priority_score;
    rawLevel = rawLevel.level ?? rawLevel.priority_level;
  }

  if (!rawLevel || typeof rawLevel !== 'string') return null;

  const upper = rawLevel.toUpperCase();
  const colorClass = getPriorityColor(upper);
  const label = PRIORITY_LEVELS[upper]?.label || rawLevel;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colorClass}`}>
      {label}
      {rawScore !== undefined && rawScore !== null && (
        <span className="opacity-75 border-l border-current pl-1.5 ml-0.5 font-mono">
          {typeof rawScore === 'number' ? rawScore.toFixed(0) : String(rawScore)}
        </span>
      )}
    </span>
  );
};

export default PriorityBadge;
