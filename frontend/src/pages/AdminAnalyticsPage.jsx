import React, { useEffect, useState } from 'react';
import adminService from '../services/adminService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { BarChart2 } from 'lucide-react';

const COLORS = {
  category: ['#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#10b981', '#6366f1', '#ec4899', '#14b8a6', '#f97316'],
  priority: { URGENT: '#f43f5e', HIGH: '#8b5cf6', MEDIUM: '#3b82f6', LOW: '#64748b' },
  severity: { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#f59e0b', LOW: '#10b981' },
};

// Simple horizontal bar chart
const HBarChart = ({ data, colorMap = null, defaultColor = '#3b82f6', title }) => {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
      <h3 className="text-sm font-semibold text-slate-800 mb-4">{title}</h3>
      <div className="space-y-3">
        {data.map((d, i) => {
          const color = colorMap?.[d.label] || COLORS.category[i % COLORS.category.length] || defaultColor;
          const pct = (d.value / max) * 100;
          return (
            <div key={i}>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-600 capitalize truncate max-w-[60%]">
                  {d.label.replace(/_/g, ' ')}
                </span>
                <span className="font-mono font-bold text-slate-800">{d.value}</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div
                  className="h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: color }}
                />
              </div>
            </div>
          );
        })}
        {data.length === 0 && (
          <p className="text-slate-400 text-xs text-center py-4">No data available</p>
        )}
      </div>
    </div>
  );
};

// Verification funnel
const FunnelChart = ({ data, title }) => {
  const max = Math.max(...data.map((d) => d.value), 1);
  const FUNNEL_COLORS = { VERIFIED: '#10b981', NEEDS_REVIEW: '#f59e0b', REJECTED: '#ef4444', PENDING: '#94a3b8' };
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
      <h3 className="text-sm font-semibold text-slate-800 mb-4">{title}</h3>
      <div className="space-y-2">
        {data.map((d, i) => {
          const pct = (d.value / max) * 100;
          const color = FUNNEL_COLORS[d.label] || '#3b82f6';
          return (
            <div key={i} className="flex items-center gap-3">
              <div
                className="h-9 rounded-lg flex items-center justify-center text-white text-xs font-bold transition-all"
                style={{ width: `${Math.max(pct, 15)}%`, backgroundColor: color }}
              >
                {d.value}
              </div>
              <span className="text-xs text-slate-500 capitalize">{d.label.replace(/_/g, ' ')}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AdminAnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await adminService.getAnalytics();
        setAnalytics(data);
      } catch (err) {
        console.error('Failed to load analytics:', err);
        setAnalytics({});
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  if (loading) return <LoadingSpinner fullScreen />;

  const byCategory = Object.entries(analytics?.by_category || {})
    .sort(([, a], [, b]) => b - a)
    .map(([k, v]) => ({ label: k, value: v }));

  const byPriority = Object.entries(analytics?.by_priority || {})
    .map(([k, v]) => ({ label: k, value: v }));

  const bySeverity = Object.entries(analytics?.by_severity || {})
    .map(([k, v]) => ({ label: k, value: v }));

  const byVerification = Object.entries(analytics?.by_verification || {})
    .map(([k, v]) => ({ label: k, value: v }));

  const byStatus = Object.entries(analytics?.by_status || {})
    .sort(([, a], [, b]) => b - a)
    .map(([k, v]) => ({ label: k, value: v }));

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <BarChart2 size={22} className="text-blue-600" />
          Analytics
        </h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Complaint distribution, severity trends, and verification statistics
        </p>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Complaints', value: analytics?.total_complaints || 0 },
          { label: 'Avg Severity Score', value: analytics?.avg_severity_score != null ? `${analytics.avg_severity_score.toFixed(1)}` : '—' },
          { label: 'Avg Priority Score', value: analytics?.avg_priority_score != null ? `${analytics.avg_priority_score.toFixed(1)}` : '—' },
          { label: 'Resolution Rate', value: analytics?.resolution_rate != null ? `${(analytics.resolution_rate * 100).toFixed(0)}%` : '—' },
        ].map((kpi, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 text-center">
            <p className="text-2xl font-bold text-slate-900 font-mono">{kpi.value}</p>
            <p className="text-[11px] uppercase tracking-wider text-slate-400 font-medium mt-1">{kpi.label}</p>
          </div>
        ))}
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <HBarChart data={byCategory} title="Complaints by Category" />
        <HBarChart data={byPriority} colorMap={COLORS.priority} title="Priority Distribution" />
        <HBarChart data={bySeverity} colorMap={COLORS.severity} title="Severity Distribution" />
        <FunnelChart data={byVerification} title="AI Verification Outcomes" />
        <div className="lg:col-span-2">
          <HBarChart data={byStatus} title="Complaints by Lifecycle Status" />
        </div>
      </div>
    </div>
  );
};

export default AdminAnalyticsPage;
