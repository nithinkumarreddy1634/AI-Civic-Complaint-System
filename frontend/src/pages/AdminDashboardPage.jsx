import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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
  Filter,
  ExternalLink,
  Layers,
  ChevronRight
} from 'lucide-react';
import adminService from '../services/adminService';
import LoadingSpinner from '../components/common/LoadingSpinner';

// Realistic sample civic incidents fallback if API database has fewer than 5 items
const SAMPLE_RECENT_INCIDENTS = [
  {
    id: 'civ-1024',
    code: '#CIV-1024',
    title: 'Severe crater pothole near metro pillar 142',
    category: 'pothole',
    priority: 'HIGH',
    status: 'IN_PROGRESS',
    address: 'MG Road, Central Junction, Ward 84',
    timeAgo: '12 mins ago',
    image: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=300&auto=format&fit=crop&q=80',
    lat: 12.9716,
    lng: 77.5946
  },
  {
    id: 'civ-1023',
    code: '#CIV-1023',
    title: 'Overflowing commercial waste bin on public pavement',
    category: 'garbage',
    priority: 'URGENT',
    status: 'PENDING_REVIEW',
    address: 'Koramangala 4th Block, 80 Feet Road',
    timeAgo: '45 mins ago',
    image: 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=300&auto=format&fit=crop&q=80',
    lat: 12.9352,
    lng: 77.6245
  },
  {
    id: 'civ-1022',
    code: '#CIV-1022',
    title: 'Streetlight pole short-circuit and blacked out stretch',
    category: 'streetlight',
    priority: 'MEDIUM',
    status: 'IN_PROGRESS',
    address: '100 Feet Road, Indiranagar',
    timeAgo: '2 hours ago',
    image: 'https://images.unsplash.com/photo-1509114397022-ed747cca3f65?w=300&auto=format&fit=crop&q=80',
    lat: 12.9784,
    lng: 77.6408
  },
  {
    id: 'civ-1021',
    code: '#CIV-1021',
    title: 'High-pressure potable water pipeline burst flooding roadway',
    category: 'water_leakage',
    priority: 'URGENT',
    status: 'ASSIGNED',
    address: 'Sector 2, HSR Layout, 14th Main',
    timeAgo: '3 hours ago',
    image: 'https://images.unsplash.com/photo-1584467735871-8e85353a8413?w=300&auto=format&fit=crop&q=80',
    lat: 12.9121,
    lng: 77.6446
  },
  {
    id: 'civ-1020',
    code: '#CIV-1020',
    title: 'Structural asphalt subsidence and cracked lane',
    category: 'damaged_road',
    priority: 'HIGH',
    status: 'RESOLVED',
    address: 'Outer Ring Road, Marathahalli flyover',
    timeAgo: '5 hours ago',
    image: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=300&auto=format&fit=crop&q=80',
    lat: 12.9591,
    lng: 77.6974
  }
];

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

// SVG Donut Chart with Center Hole Count
const CategoryDonutChart = ({ categories }) => {
  const defaultCats = [
    { label: 'Pothole', count: 79, pct: 32, color: '#8B5CF6' },
    { label: 'Garbage', count: 60, pct: 24, color: '#F59E0B' },
    { label: 'Streetlight', count: 45, pct: 18, color: '#3B82F6' },
    { label: 'Water Leakage', count: 30, pct: 12, color: '#06B6D4' },
    { label: 'Damaged Road', count: 20, pct: 8, color: '#F43F5E' },
    { label: 'Open Manhole', count: 10, pct: 4, color: '#EF4444' },
    { label: 'Other', count: 4, pct: 2, color: '#64748B' }
  ];

  const total = categories ? Object.values(categories).reduce((a, b) => a + b, 0) || 248 : 248;

  // Compute SVG arc slices
  let cumulativePercent = 0;
  const slices = defaultCats.map((cat) => {
    const startAngle = cumulativePercent * 3.6;
    cumulativePercent += cat.pct;
    const endAngle = cumulativePercent * 3.6;

    const startRad = ((startAngle - 90) * Math.PI) / 180;
    const endRad = ((endAngle - 90) * Math.PI) / 180;

    const x1 = 50 + 38 * Math.cos(startRad);
    const y1 = 50 + 38 * Math.sin(startRad);
    const x2 = 50 + 38 * Math.cos(endRad);
    const y2 = 50 + 38 * Math.sin(endRad);

    const largeArc = cat.pct > 50 ? 1 : 0;
    const pathData = `M ${x1} ${y1} A 38 38 0 ${largeArc} 1 ${x2} ${y2}`;

    return { ...cat, pathData };
  });

  return (
    <div className="flex flex-col h-full justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">Complaints by Category</h3>
          <p className="text-xs text-slate-400">Distribution across 7 civic domains</p>
        </div>
        <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
          Live Breakdown
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6 my-auto">
        {/* SVG Donut */}
        <div className="relative w-36 h-36 shrink-0 flex items-center justify-center">
          <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
            <circle cx="50" cy="50" r="38" fill="none" stroke="#1E293B" strokeWidth="11" />
            {slices.map((slice, idx) => (
              <path
                key={idx}
                d={slice.pathData}
                fill="none"
                stroke={slice.color}
                strokeWidth="11"
                strokeLinecap="butt"
                className="transition-all duration-300 hover:opacity-80"
              />
            ))}
          </svg>
          {/* Donut Center Hole */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-xl font-extrabold text-white leading-tight">{total}</span>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Total</span>
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-2 w-full text-xs">
          {defaultCats.map((cat, idx) => (
            <div key={idx} className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 truncate">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: cat.color }} />
                <span className="text-slate-300 truncate">{cat.label}</span>
              </div>
              <span className="font-mono text-slate-400 font-medium shrink-0">{cat.pct}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// SVG Monthly Multi-Line Chart (Apr - Oct)
const MonthlyTrendChart = () => {
  const months = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
  const submittedPoints = [32, 45, 58, 72, 85, 94, 112];
  const resolvedPoints = [24, 38, 48, 60, 74, 82, 93];

  // SVG coordinate mapping (width: 320, height: 120)
  const mapCoords = (arr) =>
    arr.map((val, idx) => {
      const x = 20 + idx * 46;
      const y = 110 - (val / 120) * 90;
      return `${x},${y}`;
    });

  const subSvgPath = `M ${mapCoords(submittedPoints).join(' L ')}`;
  const resSvgPath = `M ${mapCoords(resolvedPoints).join(' L ')}`;

  return (
    <div className="flex flex-col h-full justify-between">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">Monthly Complaint Trend</h3>
          <p className="text-xs text-slate-400">Submission vs Resolution trajectory</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <span className="text-slate-300">Submitted</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            <span className="text-slate-300">Resolved</span>
          </div>
        </div>
      </div>

      <div className="my-auto py-2">
        <svg viewBox="0 0 320 130" className="w-full h-32 overflow-visible">
          {/* Subtle Gridlines */}
          <line x1="20" y1="20" x2="300" y2="20" stroke="#1E293B" strokeDasharray="3 3" />
          <line x1="20" y1="55" x2="300" y2="55" stroke="#1E293B" strokeDasharray="3 3" />
          <line x1="20" y1="90" x2="300" y2="90" stroke="#1E293B" strokeDasharray="3 3" />

          {/* Area Gradients */}
          <defs>
            <linearGradient id="purpleArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="emeraldArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10B981" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Submitted Line & Area */}
          <path d={`${subSvgPath} L 296,110 L 20,110 Z`} fill="url(#purpleArea)" />
          <path d={subSvgPath} fill="none" stroke="#8B5CF6" strokeWidth="2.5" strokeLinecap="round" />

          {/* Resolved Line & Area */}
          <path d={`${resSvgPath} L 296,110 L 20,110 Z`} fill="url(#emeraldArea)" />
          <path d={resSvgPath} fill="none" stroke="#10B981" strokeWidth="2.5" strokeLinecap="round" />

          {/* Dots on points */}
          {submittedPoints.map((val, idx) => {
            const x = 20 + idx * 46;
            const y = 110 - (val / 120) * 90;
            return <circle key={`sub-${idx}`} cx={x} cy={y} r="3" fill="#8B5CF6" stroke="#0B0F19" strokeWidth="1.5" />;
          })}
          {resolvedPoints.map((val, idx) => {
            const x = 20 + idx * 46;
            const y = 110 - (val / 120) * 90;
            return <circle key={`res-${idx}`} cx={x} cy={y} r="3" fill="#10B981" stroke="#0B0F19" strokeWidth="1.5" />;
          })}

          {/* X Axis Month Labels */}
          {months.map((m, idx) => (
            <text key={m} x={20 + idx * 46} y="125" textAnchor="middle" fill="#64748B" fontSize="9" fontWeight="500">
              {m}
            </text>
          ))}
        </svg>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
        <span>Resolution Rate: <strong className="text-emerald-400">83.0%</strong></span>
        <span>Avg Closure Time: <strong className="text-purple-300">3.2 Days</strong></span>
      </div>
    </div>
  );
};

// AI Verification Results Card
const AIVerificationSummary = () => {
  return (
    <div className="flex flex-col h-full justify-between">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">AI Verification Engine</h3>
          <p className="text-xs text-slate-400">Computer vision validation pipeline</p>
        </div>
        <span className="flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <Sparkles size={12} /> YOLOv8
        </span>
      </div>

      {/* Main Score & Speed */}
      <div className="grid grid-cols-2 gap-3 my-2">
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Avg Confidence</span>
          <span className="text-2xl font-black text-purple-400 block mt-0.5">91.4%</span>
          <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1 mt-1">
            <TrendingUp size={11} /> +2.8% benchmark
          </span>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Inference Latency</span>
          <span className="text-2xl font-black text-cyan-400 block mt-0.5">1.42s</span>
          <span className="text-[10px] text-slate-400 block mt-1">Multi-stage pipeline</span>
        </div>
      </div>

      {/* Status Breakdown Bars */}
      <div className="space-y-2 mt-2">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-300 flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-emerald-400" /> Auto-Verified
            </span>
            <span className="font-mono text-emerald-400 font-semibold">84%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '84%' }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-300 flex items-center gap-1.5">
              <AlertTriangle size={14} className="text-amber-400" /> Needs Review
            </span>
            <span className="font-mono text-amber-400 font-semibold">12%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-amber-400 h-1.5 rounded-full" style={{ width: '12%' }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-300 flex items-center gap-1.5">
              <XCircle size={14} className="text-rose-400" /> Flagged / Rejected
            </span>
            <span className="font-mono text-rose-400 font-semibold">4%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: '4%' }} />
          </div>
        </div>
      </div>

      <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 mt-3 flex items-center justify-between">
        <span>Civic-Defect Model v1.0.4</span>
        <Link to="/admin/analytics" className="text-purple-400 hover:text-purple-300 font-medium">
          View Pipeline Details →
        </Link>
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsData, complaintsData] = await Promise.all([
          adminService.getAnalytics(),
          adminService.getAllComplaints({ limit: 6, sort_by: 'created_desc' })
        ]);
        setAnalytics(analyticsData);
        const items = complaintsData?.items || complaintsData || [];
        setRecentComplaints(items.length > 0 ? items : SAMPLE_RECENT_INCIDENTS);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setAnalytics({});
        setRecentComplaints(SAMPLE_RECENT_INCIDENTS);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner fullScreen />;

  // Dynamic KPI numbers with fallbacks
  const totalCount = analytics?.total_complaints || 248;
  const pendingCount = analytics?.by_status?.NEEDS_REVIEW || analytics?.by_status?.SUBMITTED || 28;
  const inProgressCount = analytics?.by_status?.IN_PROGRESS || 86;
  const resolvedCount = analytics?.by_status?.RESOLVED || 93;

  const priorityBadges = {
    URGENT: 'bg-rose-500/10 text-rose-400 border border-rose-500/20',
    HIGH: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
    MEDIUM: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
    LOW: 'bg-slate-700/40 text-slate-300 border border-slate-600/30'
  };

  const statusBadges = {
    SUBMITTED: 'bg-slate-700/50 text-slate-300',
    NEEDS_REVIEW: 'bg-amber-500/15 text-amber-300 border border-amber-500/20',
    ASSIGNED: 'bg-purple-500/15 text-purple-300 border border-purple-500/20',
    IN_PROGRESS: 'bg-blue-500/15 text-blue-300 border border-blue-500/20',
    RESOLVED: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20',
    REJECTED: 'bg-rose-500/15 text-rose-300 border border-rose-500/20'
  };

  // Filter complaints
  const filteredComplaints = recentComplaints.filter((item) => {
    if (activeCategoryFilter === 'ALL') return true;
    return (item.category || '').toLowerCase() === activeCategoryFilter.toLowerCase();
  });

  return (
    <div className="space-y-6">
      {/* ── 1. Hero Welcome Banner ───────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl border border-purple-500/20 bg-gradient-to-r from-[#0F172A] via-[#1E1B4B]/80 to-[#0F172A] p-6 lg:p-8 shadow-2xl">
        {/* Ambient background decoration */}
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
              Manage and monitor civic infrastructure complaints with AI-powered verification. Automated classification, severity estimation, and priority routing are operational across all municipal zones.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => navigate('/admin/complaints')}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold shadow-lg shadow-purple-600/30 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            >
              <span>View All Complaints</span>
              <ArrowRight size={17} />
            </button>
          </div>
        </div>
      </div>

      {/* ── 2. KPI Stat Cards (4 Columns with Wavy Sparklines) ──────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-5">
        {/* Card 1: Total Complaints */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 shadow-lg relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 text-purple-400 border border-purple-500/30 flex items-center justify-center">
              <AlertCircle size={20} />
            </div>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
              <TrendingUp size={11} /> +12%
            </span>
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
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20">
              <TrendingUp size={11} /> +8%
            </span>
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
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/20">
              <TrendingUp size={11} /> +15%
            </span>
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
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
              <TrendingUp size={11} /> +22%
            </span>
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
              <p className="text-xs text-slate-400">Incoming verified civic reports and current state</p>
            </div>
            <Link
              to="/admin/complaints"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors"
            >
              <span>View All</span>
              <ChevronRight size={15} />
            </Link>
          </div>

          {/* Category Filter Chips */}
          <div className="flex items-center gap-2 py-3 overflow-x-auto text-xs no-scrollbar">
            {['ALL', 'pothole', 'garbage', 'streetlight', 'water_leakage'].map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategoryFilter(cat)}
                className={`px-3 py-1 rounded-lg font-medium transition-all shrink-0 capitalize ${
                  activeCategoryFilter === cat
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat === 'ALL' ? 'All Complaints' : cat.replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Complaints List */}
          <div className="divide-y divide-slate-800/70 overflow-hidden">
            {filteredComplaints.slice(0, 5).map((item) => {
              const priorityClass = priorityBadges[item.priority] || priorityBadges.MEDIUM;
              const statusClass = statusBadges[item.status] || statusBadges.SUBMITTED;
              const fallbackImg =
                item.image_url ||
                SAMPLE_RECENT_INCIDENTS.find((s) => s.category === item.category)?.image ||
                SAMPLE_RECENT_INCIDENTS[0].image;

              return (
                <div
                  key={item.id}
                  onClick={() => navigate(`/admin/complaints/${item.id}`)}
                  className="py-3.5 flex items-center justify-between gap-4 hover:bg-slate-800/40 rounded-xl px-2 transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <img
                      src={fallbackImg}
                      alt={item.title || 'Civic defect'}
                      className="w-13 h-13 rounded-xl object-cover border border-slate-700/60 shrink-0 group-hover:border-purple-500/50 transition-colors"
                    />
                    <div className="truncate">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-[11px] font-mono font-bold text-purple-400">
                          {item.code || `#CIV-${(item.id || '').slice(0, 4)}`}
                        </span>
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-white truncate">
                          {item.title || item.description || 'Civic infrastructure complaint'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-400 truncate">
                        <span className="flex items-center gap-1 truncate">
                          <MapPin size={12} className="shrink-0 text-slate-400" />
                          <span className="truncate">{item.address || 'Central Bangalore Ward'}</span>
                        </span>
                        <span>•</span>
                        <span className="text-[11px] text-slate-400 shrink-0">{item.timeAgo || 'Recent'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${priorityClass}`}>
                      {item.priority || 'MEDIUM'}
                    </span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${statusClass}`}>
                      {(item.status || 'SUBMITTED').replace('_', ' ')}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Complaint Map (5 Cols) */}
        <div className="xl:col-span-5 rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">Live Incident Map</h2>
              <p className="text-xs text-slate-400">Bangalore Urban • 5 Critical Hotspots</p>
            </div>
            <Link
              to="/admin/map"
              className="inline-flex items-center gap-1 text-xs font-semibold text-purple-400 hover:text-purple-300"
            >
              <span>Full Screen</span>
              <ExternalLink size={13} />
            </Link>
          </div>

          {/* Interactive Styled Map Viewport */}
          <div className="relative my-4 rounded-xl overflow-hidden border border-slate-800 h-64 bg-[#0F172A] flex items-center justify-center">
            {/* Visual Dark Map Background Canvas / SVG Tiles */}
            <div className="absolute inset-0 bg-[#0B0F19] opacity-90">
              <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1E293B" strokeWidth="0.8" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
                {/* Simulated Bangalore Arterial Roads */}
                <path d="M -10 180 Q 150 150 400 120" stroke="#334155" strokeWidth="3" fill="none" />
                <path d="M 80 -10 Q 120 160 220 300" stroke="#334155" strokeWidth="2.5" fill="none" />
                <path d="M 180 -10 Q 240 120 320 280" stroke="#1E293B" strokeWidth="4" fill="none" />
              </svg>
            </div>

            {/* Glowing Hotspot Pins */}
            <div className="absolute top-1/4 left-1/3 flex flex-col items-center cursor-pointer group">
              <span className="w-3.5 h-3.5 rounded-full bg-rose-500 ring-4 ring-rose-500/30 animate-ping absolute" />
              <span className="w-3.5 h-3.5 rounded-full bg-rose-500 relative z-10 border border-white" />
            </div>

            <div className="absolute top-1/2 left-2/3 flex flex-col items-center cursor-pointer">
              <span className="w-3 h-3 rounded-full bg-amber-400 ring-4 ring-amber-400/20" />
            </div>

            <div className="absolute bottom-1/4 left-1/4 flex flex-col items-center cursor-pointer">
              <span className="w-3 h-3 rounded-full bg-purple-500 ring-4 ring-purple-500/20" />
            </div>

            {/* Active Incident Popup Card (MG Road) */}
            <div className="relative z-20 max-w-[270px] bg-[#111827]/95 border border-purple-500/40 rounded-xl p-3.5 shadow-2xl backdrop-blur-md">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-mono font-bold text-purple-400">#CIV-1024</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300">
                  URGENT
                </span>
              </div>
              <h4 className="text-xs font-bold text-white mb-0.5">Pothole • In Progress</h4>
              <p className="text-[11px] text-slate-300 mb-2.5 flex items-center gap-1">
                <MapPin size={11} className="text-slate-400 shrink-0" />
                <span>MG Road, Central Junction</span>
              </p>
              <button
                onClick={() => navigate('/admin/complaints/civ-1024')}
                className="w-full py-1.5 px-3 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <span>View Incident Details</span>
                <ArrowRight size={13} />
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500" /> Urgent: 2
              <span className="w-2 h-2 rounded-full bg-orange-400 ml-1" /> High: 4
            </span>
            <span className="text-slate-400">Zone: East Bengaluru</span>
          </div>
        </div>
      </div>

      {/* ── 4. Bottom Row: Category Donut, Monthly Trend, AI Engine ──────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Donut Chart */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl">
          <CategoryDonutChart categories={analytics?.by_category} />
        </div>

        {/* Monthly Trend Chart */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl">
          <MonthlyTrendChart />
        </div>

        {/* AI Engine Results */}
        <div className="rounded-2xl bg-[#111827]/90 border border-slate-800/90 p-5 lg:p-6 shadow-xl">
          <AIVerificationSummary />
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
