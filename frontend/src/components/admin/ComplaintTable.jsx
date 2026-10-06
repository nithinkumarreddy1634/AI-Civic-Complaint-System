import React from 'react';
import { formatDate, truncateText, getCategoryMeta, getImageUrl } from '../../utils/helpers';
import StatusBadge from '../common/StatusBadge';
import PriorityBadge from '../ai/PriorityBadge';
import SeverityBadge from '../ai/SeverityBadge';
import { ExternalLink } from 'lucide-react';

const ComplaintTable = ({ complaints = [], onRowClick }) => {
  return (
    <div className="overflow-x-auto bg-white rounded-xl shadow-sm border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Complaint</th>
            <th className="px-4 py-3 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Status</th>
            <th className="px-4 py-3 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Priority</th>
            <th className="px-4 py-3 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Severity</th>
            <th className="px-4 py-3 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Date</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-100">
          {complaints.length === 0 ? (
            <tr>
              <td colSpan="6" className="px-6 py-10 text-center text-slate-400 text-sm">
                No complaints found.
              </td>
            </tr>
          ) : (
            complaints.map((complaint) => {
              const meta = getCategoryMeta(complaint.category);
              const CategoryIcon = meta.icon;
              const imgUrl = getImageUrl(complaint.image_path);

              return (
                <tr
                  key={complaint.id}
                  onClick={() => onRowClick && onRowClick(complaint.id)}
                  className="hover:bg-slate-50 cursor-pointer transition-colors"
                >
                  {/* Complaint cell with thumbnail */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg overflow-hidden bg-slate-100 shrink-0">
                        {imgUrl ? (
                          <img src={imgUrl} alt="complaint" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <CategoryIcon size={18} className="text-slate-400" />
                          </div>
                        )}
                      </div>
                      <div className="min-w-0">
                        <div className={`text-xs font-semibold mb-0.5 ${meta.color || 'text-slate-700'}`}>
                          {meta.label}
                        </div>
                        <p className="text-slate-600 text-xs truncate max-w-[180px]">
                          {truncateText(complaint.description, 60)}
                        </p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">#{String(complaint.id).substring(0, 8)}</p>
                      </div>
                    </div>
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap">
                    <StatusBadge status={complaint.status} size="xs" />
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap">
                    {(complaint.priority_level || complaint.priority?.level)
                      ? <PriorityBadge level={complaint.priority_level || complaint.priority?.level} score={complaint.priority?.score} />
                      : <span className="text-slate-300 text-xs">—</span>}
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap">
                    {(complaint.severity?.level)
                      ? <SeverityBadge level={complaint.severity.level} score={complaint.severity.score} />
                      : <span className="text-slate-300 text-xs">—</span>}
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-500">
                    {formatDate(complaint.created_at)}
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap">
                    <ExternalLink size={14} className="text-slate-400 hover:text-blue-600 transition-colors" />
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ComplaintTable;
