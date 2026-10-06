import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Calendar } from 'lucide-react';
import { formatDate, truncateText, getPriorityColor, getCategoryMeta, getImageUrl } from '../../utils/helpers';
import StatusBadge from '../common/StatusBadge';

const ComplaintCard = ({ complaint }) => {
  const categoryMeta = getCategoryMeta(complaint.category);
  const CategoryIcon = categoryMeta?.icon || MapPin;
  const imgUrl = getImageUrl(complaint.image_path);

  return (
    <Link
      to={`/complaints/${complaint.id}`}
      className="flex flex-col bg-[#111827]/90 rounded-2xl shadow-xl border border-slate-800 hover:border-purple-500/50 hover:shadow-purple-900/10 transition-all duration-200 overflow-hidden group"
    >
      {/* Image thumbnail */}
      <div className="h-44 bg-slate-900 relative overflow-hidden">
        {imgUrl ? (
          <img
            src={imgUrl}
            alt={categoryMeta?.label || 'Complaint'}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 gap-2">
            <CategoryIcon size={32} className="opacity-30" />
            <span className="text-xs">No image available</span>
          </div>
        )}
        {/* Status badge overlay */}
        <div className="absolute top-3 right-3">
          <StatusBadge status={complaint.status} />
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col flex-1">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 text-purple-300 border border-slate-700/80">
            <CategoryIcon size={13} className="text-purple-400" />
            <span>{categoryMeta?.label || complaint.category}</span>
          </div>
          {complaint.priority_level && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${getPriorityColor(complaint.priority_level)}`}>
              {complaint.priority_level}
            </span>
          )}
        </div>

        <p className="text-slate-300 text-sm leading-snug flex-1 line-clamp-2 mb-3">
          {truncateText(complaint.description, 110)}
        </p>

        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2.5 border-t border-slate-800">
          <div className="flex items-center gap-1 min-w-0">
            <MapPin size={12} className="shrink-0 text-slate-400" />
            <span className="truncate max-w-[120px]">
              {complaint.address || (complaint.latitude != null ? `${Number(complaint.latitude).toFixed(3)}, ${Number(complaint.longitude).toFixed(3)}` : 'Location provided')}
            </span>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <Calendar size={12} />
            <span>{formatDate(complaint.created_at)}</span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ComplaintCard;
