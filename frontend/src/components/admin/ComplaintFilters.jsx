import React from 'react';
import { COMPLAINT_CATEGORIES, COMPLAINT_STATUSES, PRIORITY_LEVELS, SEVERITY_LEVELS } from '../../utils/constants';
import { X } from 'lucide-react';

const SELECT_CLASS = 'w-full text-sm bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all';

const ComplaintFilters = ({ filters, onFilterChange }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...filters, [name]: value || undefined };
    // Remove undefined keys
    Object.keys(updated).forEach((k) => { if (!updated[k]) delete updated[k]; });
    onFilterChange(updated);
  };

  const hasFilters = Object.values(filters).some((v) => v);

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 mb-5">
      <div className="flex flex-wrap gap-3 items-end">
        {/* Status */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Status</label>
          <select name="status" value={filters.status || ''} onChange={handleChange} className={SELECT_CLASS}>
            <option value="">All Statuses</option>
            {Object.entries(COMPLAINT_STATUSES).map(([key, v]) => (
              <option key={key} value={key}>{v.label}</option>
            ))}
          </select>
        </div>

        {/* Category */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Category</label>
          <select name="category" value={filters.category || ''} onChange={handleChange} className={SELECT_CLASS}>
            <option value="">All Categories</option>
            {COMPLAINT_CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
        </div>

        {/* Priority */}
        <div className="flex-1 min-w-[130px]">
          <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Priority</label>
          <select name="priority_level" value={filters.priority_level || ''} onChange={handleChange} className={SELECT_CLASS}>
            <option value="">All Priorities</option>
            {Object.keys(PRIORITY_LEVELS).map((key) => (
              <option key={key} value={key}>{PRIORITY_LEVELS[key].label}</option>
            ))}
          </select>
        </div>

        {/* Severity */}
        <div className="flex-1 min-w-[130px]">
          <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Severity</label>
          <select name="severity_level" value={filters.severity_level || ''} onChange={handleChange} className={SELECT_CLASS}>
            <option value="">All Severities</option>
            {Object.keys(SEVERITY_LEVELS).map((key) => (
              <option key={key} value={key}>{SEVERITY_LEVELS[key].label}</option>
            ))}
          </select>
        </div>

        {/* Verification */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Verification</label>
          <select name="verification_status" value={filters.verification_status || ''} onChange={handleChange} className={SELECT_CLASS}>
            <option value="">All</option>
            <option value="VERIFIED">Verified</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>

        {/* Sort By */}
        <div className="flex-1 min-w-[150px]">
          <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Sort By</label>
          <select name="sort_by" value={filters.sort_by || 'created_desc'} onChange={handleChange} className={SELECT_CLASS}>
            <option value="created_desc">Newest First</option>
            <option value="created_asc">Oldest First</option>
            <option value="priority_desc">Highest Priority</option>
            <option value="priority_asc">Lowest Priority</option>
            <option value="severity_desc">Highest Severity</option>
          </select>
        </div>

        {/* Clear */}
        {hasFilters && (
          <button
            onClick={() => onFilterChange({})}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 text-slate-600 rounded-lg text-sm font-medium hover:bg-slate-200 transition-colors"
          >
            <X size={14} />
            Clear
          </button>
        )}
      </div>
    </div>
  );
};

export default ComplaintFilters;
