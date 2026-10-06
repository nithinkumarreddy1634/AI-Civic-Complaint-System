import React from 'react';
import { formatStatus, getStatusColor } from '../../utils/helpers';

const StatusBadge = ({ status, size = 'sm' }) => {
  if (!status) return null;

  const colorClass = getStatusColor(status);
  const label = formatStatus(status);
  const sizeClass = size === 'xs' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-0.5 text-xs';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium border ${colorClass} ${sizeClass}`}
    >
      {label}
    </span>
  );
};

export default StatusBadge;
