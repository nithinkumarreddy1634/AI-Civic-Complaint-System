import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import {
  AlertCircle,
  Clock,
  Activity,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  MapPin,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  ExternalLink,
  ChevronRight,
  PlusCircle,
} from 'lucide-react';
import adminService from '../services/adminService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getImageUrl, formatDate } from '../utils/helpers';

// Leaflet map controller for mini incident viewport
const MiniMapController = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 200);
    if (center && center[0] != null && center[1] != null) {
      map.setView(center, 12);
    }
    return () => clearTimeout(timer);
  }, [map, center]);
  return null;
};

// Sparkline SVG Component
const Sparkline = ({ strokeColor, fillGradientId, points }) => (
  <svg viewBox="0 0 120 40" className="w-full h-10 overflow-visible">
    <defs>
      <linearGradient id={fillGradientId} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={strokeColor} stopOpacity="0.35" />
        <stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
      </linearGradient>
    </defs>
    <path
      d={`M 0,35 Q 20,${points[0]} 40,${points[1]} T 80,${points[2]} T 120,${points[3]} L 120,40 L 0,40 Z`}
      fill={`url(#${fillGradientId})`}
    />
    <path
      d={`M 0,35 Q 20,${points[0]} 40,${points[1]} T 80,${points[2]} T 120,${points[3]}`}
      fill="none"
      stroke={strokeColor}
      strokeWidth="2.5"
      strokeLinecap="round"
    />
  </svg>
);

// Dynamic Category Donut Chart from Real Database Metrics
const CategoryDonutChart = ({ categories = {} }) => {
  const COLOR_PALETTE = ['#8B5CF6', '#F59E0B', '#3B82F6', '#06B6D4', '#F43F5E', '#10B981', '#EC4899', '#64748B'];
  const entries = Object.entries(categories || {}).filter(([_, count]) => count > 0);
  const total = entries.reduce((acc, [_, count]) => acc + count, 0);

  const cats = entries.length > 0
    ? entries.map(([cat, count], idx) => ({
        label: cat.replace(/_/g, ' '),
        count,
        pct: total > 0 ? Math.round((count / total) * 100) : 0,
        color: COLOR_PALETTE[idx % COLOR_PALETTE.length],
      }))
    : [{ label: 'No complaints yet', count: 0, pct: 100, color: '#334155' }];

  let cumulativePercent = 0;
  const slices = cats.map((cat) => {
    const startAngle = cumulativePercent * 3.6;
    cumulativePercent += cat.pct;
    const endAngle = Math.min(cumulativePercent * 3.6, 359.99);

    const startRad = ((startAngle - 90) * Math.PI) / 180;
    const endRad = ((endAngle - 90) * Math.PI) / 180;

    const x1 = 50 + 38 * Math.cos(startRad);
    const y1 = 50 + 38 * Math.sin(startRad);
    const x2 = 50 + 38 * Math.cos(endRad);
    const y2 = 50 + 38 * Math.sin(endRad);

    const largeArc = cat.pct > 50 ? 1 : 0;
    const pathData = total > 0 ? `M ${x1} ${y1} A 38 38 0 ${largeArc} 1 ${x2} ${y2}` : '';

    return { ...cat, pathData };
  });

  return (
    <div className="flex flex-col h-full justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">Complaints by Category</h3>
          <p className="text-xs text-slate-400">Real distribution across civic domains</p>
        </div>
        <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
          Live Database
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6 my-auto">
        {/* SVG Donut */}
        <div className="relative w-36 h-36 shrink-0 flex items-center justify-center">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            <circle cx="50" cy="50" r="38" fill="none" stroke="#1E293B" strokeWidth="11" />
            {slices.map((slice, idx) =>
              slice.pathData ? (
                <path
                  key={idx}
                  d={slice.pathData}
                  fill="none"
                  stroke={slice.color}
                  strokeWidth="11"
                  strokeLinecap="butt"
                  className="transition-all duration-300 hover:opacity-80"
                />
              ) : null
            )}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-xl font-extrabold text-white leading-tight">{total}</span>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Total</span>
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-2 w-full text-xs">
          {cats.map((cat, idx) => (
            <div key={idx} className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 truncate">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: cat.color }} />
                <span className="text-slate-300 truncate capitalize">{cat.label}</span>
              </div>
              <span className="font-mono text-slate-400 font-medium shrink-0">{cat.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Real Lifecycle Status Distribution Chart
const StatusDistributionChart = ({ byStatus = {} }) => {
  const statusItems = [
    { key: 'SUBMITTED', label: 'Submitted', color: '#64748B' },
    { key: 'AI_PROCESSING', label: 'AI Processing', color: '#F59E0B' },
    { key: 'VERIFIED', label: 'Verified', color: '#3B82F6' },
    { key: 'NEEDS_REVIEW', label: 'Needs Review', color: '#F97316' },
    { key: 'ASSIGNED', label: 'Assigned', color: '#8B5CF6' },
    { key: 'IN_PROGRESS', label: 'In Progress', color: '#06B6D4' },
    { key: 'RESOLVED', label: 'Resolved', color: '#10B981' },
    { key: 'REJECTED', label: 'Rejected', color: '#F43F5E' },
  ];

  const total = Object.values(byStatus).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="flex flex-col h-full justify-between">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">Lifecycle Status Distribution</h3>
          <p className="text-xs text-slate-400">Current workflow breakdown</p>
        </div>
        <span className="text-[11px] font-mono text-purple-400">Real-Time</span>
      </div>

      <div className="space-y-2.5 my-auto py-2">
        {statusItems.map((s) => {
          const count = byStatus[s.key] || 0;
          const pct = Math.round((count / total) * 100);
          return (
            <div key={s.key} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
                  {s.label}
                </span>
                <span className="font-mono text-slate-400">
                  {count} <span className="text-slate-500 text-[10px]">({pct}%)</span>
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(pct, count > 0 ? 3 : 0)}%`, backgroundColor: s.color }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
        <span>Active Workflow Total: <strong className="text-white">{total > 1 ? total : 0}</strong></span>
        <span>Resolved: <strong className="text-emerald-400">{byStatus.RESOLVED || 0}</strong></span>
      </div>
    </div>
  );
};

// Real AI Verification Engine Summary Card
const AIVerificationSummary = ({ analytics = {} }) => {
  const verified = analytics?.by_verification?.VERIFIED || 0;
  const needsReview = analytics?.by_verification?.NEEDS_REVIEW || 0;
  const rejected = analytics?.by_verification?.REJECTED || 0;
  const total = verified + needsReview + rejected || analytics?.total_complaints || 0;

  const verifiedPct = total > 0 ? Math.round((verified / total) * 100) : 0;
  const reviewPct = total > 0 ? Math.round((needsReview / total) * 100) : 0;
  const rejectedPct = total > 0 ? Math.round((rejected / total) * 100) : 0;

  const avgSeverity = analytics?.avg_severity_score != null ? `${analytics.avg_severity_score.toFixed(1)}/100` : '—';
  const avgPriority = analytics?.avg_priority_score != null ? `${analytics.avg_priority_score.toFixed(1)}/100` : '—';

  return (
    <div className="flex flex-col h-full justify-between">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">AI Verification Pipeline</h3>
          <p className="text-xs text-slate-400">YOLOv8 vision & severity audit outcomes</p>
        </div>
        <span className="flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <Sparkles size={12} /> Real Audit
        </span>
      </div>

      {/* Main KPI Scores from DB */}
      <div className="grid grid-cols-2 gap-3 my-2">
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Avg Severity</span>
          <span className="text-2xl font-black text-purple-400 block mt-0.5">{avgSeverity}</span>
          <span className="text-[10px] text-slate-400 block mt-1">Multi-factor impact</span>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Avg Priority</span>
          <span className="text-2xl font-black text-cyan-400 block mt-0.5">{avgPriority}</span>
          <span className="text-[10px] text-slate-400 block mt-1">Automated ranking</span>
        </div>
      </div>

      {/* Real Breakdown Bars */}
      <div className="space-y-2 mt-2">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-300 flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-emerald-400" /> Auto-Verified
            </span>
            <span className="font-mono text-emerald-400 font-semibold">
              {verified} ({verifiedPct}%)
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${verifiedPct}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-300 flex items-center gap-1.5">
              <AlertTriangle size={14} className="text-amber-400" /> Needs Review
            </span>
            <span className="font-mono text-amber-400 font-semibold">
              {needsReview} ({reviewPct}%)
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-amber-400 h-1.5 rounded-full" style={{ width: `${reviewPct}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-300 flex items-center gap-1.5">
              <XCircle size={14} className="text-rose-400" /> Flagged / Rejected
            </span>
            <span className="font-mono text-rose-400 font-semibold">
              {rejected} ({rejectedPct}%)
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: `${rejectedPct}%` }} />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
        <span>Audited Total: <strong className="text-white">{total}</strong></span>
        <span>Resolution Rate: <strong className="text-emerald-400">
          {analytics?.resolution_rate != null ? `${(analytics.resolution_rate * 100).toFixed(0)}%` : '—'}
        </strong></span>
      </div>
    </div>
  );
};

const AdminDashboardPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [recentComplaints, setRecentComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('ALL');
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const [dashboardData, analyticsData, complaintsData] = await Promise.all([
        adminService.getDashboard().catch(() => null),
        adminService.getAnalytics().catch(() => null),
        adminService.getAllComplaints({ limit: 10, sort_by: 'created_desc' }).catch(() => null),
      ]);
      const merged = {
        ...(dashboardData || {}),
        ...(analyticsData || {}),
        total_complaints: dashboardData?.total_complaints ?? analyticsData?.total_complaints,
        by_status: dashboardData?.by_status || analyticsData?.by_status || {},
        by_category: dashboardData?.by_category || analyticsData?.by_category || {},
      };
      setAnalytics(merged);
      const items = complaintsData?.items || complaintsData || [];
      setRecentComplaints(Array.isArray(items) ? items : []);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setAnalytics({});
      setRecentComplaints([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner fullScreen />;

  // Real KPI numbers computed from active database
  const totalCount = analytics?.total_complaints ?? recentComplaints.length;
  const pendingCount =
    (analytics?.by_status?.NEEDS_REVIEW || 0) +
    (analytics?.by_status?.SUBMITTED || 0) +
    (analytics?.by_status?.AI_PROCESSING || 0);
  const inProgressCount =
    (analytics?.by_status?.IN_PROGRESS || 0) +
    (analytics?.by_status?.ASSIGNED || 0);
  const resolvedCount = analytics?.by_status?.RESOLVED || 0;

  const priorityBadges = {
    URGENT: 'bg-rose-500/10 text-rose-400 border border-rose-500/20',
    HIGH: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
    MEDIUM: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
    LOW: 'bg-slate-700/40 text-slate-300 border border-slate-600/30',
  };

  const statusBadges = {
    SUBMITTED: 'bg-slate-700/50 text-slate-300',
    AI_PROCESSING: 'bg-amber-500/15 text-amber-300 border border-amber-500/20',
    VERIFIED: 'bg-blue-500/15 text-blue-300 border border-blue-500/20',
    NEEDS_REVIEW: 'bg-amber-500/15 text-amber-300 border border-amber-500/20',
    ASSIGNED: 'bg-purple-500/15 text-purple-300 border border-purple-500/20',
    IN_PROGRESS: 'bg-blue-500/15 text-blue-300 border border-blue-500/20',
    RESOLVED: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20',
    REJECTED: 'bg-rose-500/15 text-rose-300 border border-rose-500/20',
  };

  // Filter complaints
  const filteredComplaints = recentComplaints.filter((item) => {
    if (activeCategoryFilter === 'ALL') return true;
    return (item.category || '').toLowerCase() === activeCategoryFilter.toLowerCase();
  });

  // Geo-tagged complaints for live incident map
  const geoComplaints = recentComplaints.filter(
    (c) => (c.latitude != null && c.longitude != null) || (c.lat != null && c.lng != null)
  );

  const mapCenter = geoComplaints.length > 0
    ? [geoComplaints[0].latitude ?? geoComplaints[0].lat, geoComplaints[0].longitude ?? geoComplaints[0].lng]
    : [12.9716, 77.5946];

  return (
    <div className="space-y-6">
      {/* ── 1. Hero Welcome Banner ───────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl border border-purple-500/20 bg-gradient-to-r from-[#0F172A] via-[#1E1B4B]/80 to-[#0F172A] p-6 lg:p-8 shadow-2xl">
        <div className="absolute right-0 top-0 -mt-12 -mr-12 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute left-1/3 bottom-0 -mb-16 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-semibold">
              <Sparkles size={13} className="text-purple-400" />
              <span>AI CIVIC INFRASTRUCTURE INTELLIGENCE</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              Welcome Back, Admin!
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Manage and monitor civic infrastructure complaints with AI-powered verification. Automated classification, severity estimation, and priority routing are operational across municipal zones.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            <button
              onClick={() => navigate('/admin/complaints/new')}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold shadow-lg shadow-purple-600/30 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            >
              <PlusCircle size={17} />
              <span>Submit Complaint</span>
            </button>
            <button
              onClick={() => navigate('/admin/complaints')}
              className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-[#161F30] hover:bg-slate-800 text-slate-200 border border-slate-700/60 text-sm font-semibold transition-all"
            >
              <span>View All</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* ── 2. Top Metric Cards ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Total Complaints */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 text-purple-400 border border-purple-500/30 flex items-center justify-center">
              <AlertCircle size={20} />
            </div>
            <span className="text-[11px] font-mono text-purple-400">Total</span>
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 block uppercase tracking-wider">Total Complaints</span>
            <span className="text-3xl font-black text-white block mt-1">{totalCount}</span>
          </div>
          <div className="mt-3 -mx-2 -mb-2">
            <Sparkline strokeColor="#8B5CF6" fillGradientId="sparkPurple" points={[25, 12, 18, 8]} />
          </div>
        </div>

        {/* Card 2: Pending Review */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/15 text-amber-400 border border-amber-500/30 flex items-center justify-center">
              <Clock size={20} />
            </div>
            <span className="text-[11px] font-mono text-amber-400">Awaiting Action</span>
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 block uppercase tracking-wider">Pending Review</span>
            <span className="text-3xl font-black text-white block mt-1">{pendingCount}</span>
          </div>
          <div className="mt-3 -mx-2 -mb-2">
            <Sparkline strokeColor="#F59E0B" fillGradientId="sparkAmber" points={[20, 28, 14, 10]} />
          </div>
        </div>

        {/* Card 3: In Progress */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
              <Activity size={20} />
            </div>
            <span className="text-[11px] font-mono text-cyan-400">Active</span>
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 block uppercase tracking-wider">In Progress</span>
            <span className="text-3xl font-black text-white block mt-1">{inProgressCount}</span>
          </div>
          <div className="mt-3 -mx-2 -mb-2">
            <Sparkline strokeColor="#06B6D4" fillGradientId="sparkCyan" points={[28, 18, 22, 6]} />
          </div>
        </div>

        {/* Card 4: Resolved */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
              <CheckCircle2 size={20} />
            </div>
            <span className="text-[11px] font-mono text-emerald-400">Closed</span>
          </div>
          <div>
            <span className="text-xs font-medium text-slate-400 block uppercase tracking-wider">Resolved</span>
            <span className="text-3xl font-black text-white block mt-1">{resolvedCount}</span>
          </div>
          <div className="mt-3 -mx-2 -mb-2">
            <Sparkline strokeColor="#10B981" fillGradientId="sparkEmerald" points={[30, 20, 12, 4]} />
          </div>
        </div>
      </div>

      {/* ── 3. Middle Section: Recent Complaints & Live Map ──────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left: Recent Complaints (7 Cols) */}
        <div className="xl:col-span-7 rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">Recent Complaints</h2>
              <p className="text-xs text-slate-400">Real incident submissions from municipal queue</p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                to="/admin/complaints/new"
                className="inline-flex items-center gap-1 text-xs font-semibold text-purple-400 hover:text-purple-300"
              >
                <PlusCircle size={14} />
                <span>Submit Complaint</span>
              </Link>
              <Link
                to="/admin/complaints"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors"
              >
                <span>View All</span>
                <ChevronRight size={15} />
              </Link>
            </div>
          </div>

          {/* Category Filter Chips */}
          <div className="flex items-center gap-2 py-3 overflow-x-auto text-xs no-scrollbar">
            {['ALL', 'pothole', 'garbage_accumulation', 'broken_streetlight', 'water_leakage', 'open_manhole'].map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategoryFilter(cat)}
                className={`px-3 py-1 rounded-lg font-medium transition-all shrink-0 capitalize ${
                  activeCategoryFilter === cat
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat === 'ALL' ? 'All Complaints' : cat.replace(/_/g, ' ')}
              </button>
            ))}
          </div>

          {/* Complaints List */}
          <div className="divide-y divide-slate-800/70 overflow-hidden flex-1">
            {filteredComplaints.length === 0 ? (
              <div className="py-12 text-center">
                <div className="w-12 h-12 rounded-xl bg-purple-600/10 text-purple-400 flex items-center justify-center mx-auto mb-3">
                  <AlertCircle size={24} />
                </div>
                <p className="text-sm font-semibold text-slate-300">No complaints found</p>
                <p className="text-xs text-slate-500 mt-1 mb-4">No civic reports filed under this category yet.</p>
                <Link
                  to="/admin/complaints/new"
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-semibold shadow-md transition-colors"
                >
                  <PlusCircle size={14} />
                  <span>Submit First Complaint</span>
                </Link>
              </div>
            ) : (
              filteredComplaints.slice(0, 5).map((item) => {
                const priorityKey =
                  (typeof item.priority === 'string' ? item.priority : null) ||
                  item.priority_level ||
                  item.priority?.priority_level ||
                  item.priority?.level ||
                  'MEDIUM';
                const priorityClass = priorityBadges[priorityKey] || priorityBadges.MEDIUM;
                const statusClass = statusBadges[item.status] || statusBadges.SUBMITTED;
                const complaintImg = getImageUrl(item.image_path) || item.image_url || '/examples/pothole.jpg';

                return (
                  <div
                    key={item.id}
                    onClick={() => navigate(`/admin/complaints/${item.id}`)}
                    className="py-3.5 flex items-center justify-between gap-4 hover:bg-slate-800/40 rounded-xl px-2 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center gap-3.5 min-w-0">
                      <img
                        src={complaintImg}
                        alt={item.title || item.category || 'Civic defect'}
                        className="w-12 h-12 rounded-xl object-cover border border-slate-700/60 shrink-0 group-hover:border-purple-500/50 transition-colors"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = '/examples/pothole.jpg';
                        }}
                      />
                      <div className="truncate">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-[11px] font-mono font-bold text-purple-400">
                            #{String(item.id || '').slice(0, 8)}
                          </span>
                          <span className="text-xs font-semibold text-slate-200 group-hover:text-white truncate">
                            {item.title || item.description || 'Civic infrastructure complaint'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-400 truncate">
                          <span className="flex items-center gap-1 truncate">
                            <MapPin size={12} className="shrink-0 text-slate-400" />
                            <span className="truncate">{item.address || 'Bengaluru Urban Ward'}</span>
                          </span>
                          <span>•</span>
                          <span className="text-[11px] text-slate-400 shrink-0">
                            {formatDate(item.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${priorityClass}`}>
                        {priorityKey}
                      </span>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${statusClass}`}>
                        {(item.status || 'SUBMITTED').replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Complaint Map (5 Cols) */}
        <div className="xl:col-span-5 rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">Live Incident Map</h2>
              <p className="text-xs text-slate-400">
                Bengaluru Urban &bull; {geoComplaints.length} Geo-Tagged Incident{geoComplaints.length !== 1 ? 's' : ''}
              </p>
            </div>
            <Link
              to="/admin/map"
              className="inline-flex items-center gap-1 text-xs font-semibold text-purple-400 hover:text-purple-300"
            >
              <span>Full Screen</span>
              <ExternalLink size={13} />
            </Link>
          </div>

          {/* Interactive Live Incident Map Viewport */}
          <div className="relative my-4 rounded-xl overflow-hidden border border-slate-800 h-64 bg-[#0F172A] z-0">
            <MapContainer
              center={mapCenter}
              zoom={12}
              style={{ height: '100%', width: '100%', zIndex: 1 }}
              scrollWheelZoom={false}
            >
              <MiniMapController center={mapCenter} />
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {geoComplaints.map((item) => {
                const lat = item.latitude ?? item.lat;
                const lng = item.longitude ?? item.lng;
                if (lat == null || lng == null) return null;

                const priorityKey =
                  (typeof item.priority === 'object' && item.priority !== null)
                    ? item.priority.priority_level || item.priority.level || 'MEDIUM'
                    : item.priority_level || item.priority || 'MEDIUM';
                const color =
                  priorityKey === 'URGENT'
                    ? '#f43f5e'
                    : priorityKey === 'HIGH'
                    ? '#8b5cf6'
                    : priorityKey === 'LOW'
                    ? '#64748b'
                    : '#3b82f6';

                return (
                  <CircleMarker
                    key={item.id}
                    center={[lat, lng]}
                    radius={priorityKey === 'URGENT' ? 10 : 8}
                    pathOptions={{
                      color: '#ffffff',
                      fillColor: color,
                      fillOpacity: 0.85,
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <div className="text-xs p-1 font-sans text-slate-800 min-w-[170px]">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-slate-900 capitalize">
                            {item.category?.replace(/_/g, ' ') || 'Incident'}
                          </span>
                          <span
                            className="px-1.5 py-0.2 rounded-full text-[9px] font-bold text-white uppercase"
                            style={{ backgroundColor: color }}
                          >
                            {priorityKey}
                          </span>
                        </div>
                        <p className="text-slate-600 mb-2 line-clamp-2">
                          {item.description || item.title || 'Civic infrastructure report'}
                        </p>
                        <button
                          type="button"
                          onClick={() => navigate(`/admin/complaints/${item.id}`)}
                          className="text-purple-600 hover:text-purple-800 font-semibold flex items-center gap-1 text-[11px]"
                        >
                          View Details &rarr;
                        </button>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500" /> Urgent:{' '}
              {geoComplaints.filter((c) => (c.priority_level || c.priority) === 'URGENT').length}
              <span className="w-2 h-2 rounded-full bg-purple-500 ml-1" /> High:{' '}
              {geoComplaints.filter((c) => (c.priority_level || c.priority) === 'HIGH').length}
            </span>
            <span className="text-slate-400">Zone: Bengaluru Urban</span>
          </div>
        </div>
      </div>

      {/* ── 4. Bottom Row: Category Donut, Status Workflow, AI Pipeline ────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real Category Donut Chart */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl">
          <CategoryDonutChart categories={analytics?.by_category} />
        </div>

        {/* Real Status Distribution */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl">
          <StatusDistributionChart byStatus={analytics?.by_status} />
        </div>

        {/* Real AI Engine Pipeline Results */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl">
          <AIVerificationSummary analytics={analytics} />
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
