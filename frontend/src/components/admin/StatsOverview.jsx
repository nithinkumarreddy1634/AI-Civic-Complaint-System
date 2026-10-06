import React from 'react';
import {
  FileText, CheckCircle2, Clock, XCircle,
  AlertTriangle, AlertOctagon, CheckSquare
} from 'lucide-react';

const StatsOverview = ({ stats }) => {
  const cards = [
    { label: 'Total', count: stats?.total || 0, icon: FileText, bg: 'bg-blue-50', icon_color: 'text-blue-600' },
    { label: 'Verified', count: stats?.verified || 0, icon: CheckCircle2, bg: 'bg-indigo-50', icon_color: 'text-indigo-600' },
    { label: 'Under Review', count: stats?.needs_review || 0, icon: Clock, bg: 'bg-amber-50', icon_color: 'text-amber-600' },
    { label: 'Rejected', count: stats?.rejected || 0, icon: XCircle, bg: 'bg-rose-50', icon_color: 'text-rose-500' },
    { label: 'Urgent', count: stats?.urgent || 0, icon: AlertOctagon, bg: 'bg-red-50', icon_color: 'text-red-600' },
    { label: 'High Priority', count: stats?.high || 0, icon: AlertTriangle, bg: 'bg-orange-50', icon_color: 'text-orange-600' },
    { label: 'Resolved', count: stats?.resolved || 0, icon: CheckSquare, bg: 'bg-emerald-50', icon_color: 'text-emerald-600' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4 mb-6">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="bg-white rounded-xl shadow-sm p-4 border border-slate-200 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow"
        >
          <div className={`p-2.5 rounded-xl mb-2 ${card.bg}`}>
            <card.icon size={22} className={card.icon_color} />
          </div>
          <span className="text-2xl font-bold text-slate-800 leading-none mb-0.5">{card.count}</span>
          <span className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">{card.label}</span>
        </div>
      ))}
    </div>
  );
};

export default StatsOverview;
