import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertCircle,
  MapPin,
  BarChart3,
  LogOut,
  Menu,
  X,
  Search,
  Bell,
  Moon,
  Sun,
  Shield,
  FileText,
  Users,
  Building2,
  Settings,
  PlusCircle,
  Layers
} from 'lucide-react';
import useAuth from '../hooks/useAuth';

const AdminLayout = () => {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(true);

  const mainNavItems = [
    { name: 'Dashboard', path: '/admin', icon: LayoutDashboard },
    { name: 'Submit Complaint', path: '/complaints/new', icon: PlusCircle },
    { name: 'All Complaints', path: '/admin/complaints', icon: AlertCircle },
    { name: 'Incident Map', path: '/admin/map', icon: MapPin },
    { name: 'Analytics', path: '/admin/analytics', icon: BarChart3 },
  ];

  const adminNavItems = [
    { name: 'Assignments', path: '/admin/complaints?filter=assigned', icon: Layers },
    { name: 'Departments', path: '/admin/analytics#departments', icon: Building2 },
    { name: 'User Management', path: '/admin/complaints', icon: Users },
    { name: 'Audit Reports', path: '/admin/analytics', icon: FileText },
  ];

  const isActive = (path) => {
    if (path === '/admin') return location.pathname === '/admin';
    return location.pathname.startsWith(path.split('?')[0]);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/admin/complaints?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  // Formatted date string matching "Oct 31, 2024 Thursday"
  const formattedDate = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    weekday: 'long',
  }).format(new Date());

  return (
    <div className="flex h-screen bg-[#0B0F19] text-slate-100 overflow-hidden font-sans">
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-[#0F172A] border-r border-slate-800/80 flex flex-col transition-all duration-300 shrink-0 z-30`}
      >
        {/* Logo & Toggle */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-800/80">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-600/30 shrink-0">
            <Shield className="text-white" size={22} />
          </div>
          {sidebarOpen && (
            <div className="truncate">
              <span className="text-base font-bold text-white tracking-wide block">CivicPulse</span>
              <span className="text-[10px] text-purple-400 font-semibold uppercase tracking-wider block">AI Infrastructure</span>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="ml-auto text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800/60 transition-colors shrink-0"
            title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {/* Main Links */}
          <nav className="space-y-1.5">
            {mainNavItems.map((item) => {
              const active = isActive(item.path);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  title={!sidebarOpen ? item.name : undefined}
                  className={`flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl transition-all duration-150 text-sm font-medium ${
                    active
                      ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                      : 'text-slate-400 hover:bg-slate-800/70 hover:text-slate-200'
                  }`}
                >
                  <Icon size={19} className="shrink-0" />
                  {sidebarOpen && <span className="truncate">{item.name}</span>}
                </Link>
              );
            })}
          </nav>

          {/* Admin Management Section */}
          <div>
            {sidebarOpen && (
              <h4 className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Administration
              </h4>
            )}
            <nav className="space-y-1">
              {adminNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.path}
                    title={!sidebarOpen ? item.name : undefined}
                    className="flex items-center gap-3.5 px-3.5 py-2 rounded-xl text-slate-400 hover:bg-slate-800/70 hover:text-slate-200 transition-all text-xs font-medium"
                  >
                    <Icon size={17} className="shrink-0 text-slate-400" />
                    {sidebarOpen && <span className="truncate">{item.name}</span>}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>

        {/* User Card & Logout */}
        <div className="p-3 border-t border-slate-800/80 bg-[#0B0F19]/40">
          {sidebarOpen ? (
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shrink-0 shadow-sm">
                  AD
                </div>
                <div className="truncate">
                  <p className="text-xs font-semibold text-slate-200 truncate">
                    {user?.name || 'Admin User'}
                  </p>
                  <p className="text-[10px] text-slate-400 truncate">
                    {user?.email || 'admin@civicpulse.gov'}
                  </p>
                </div>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-800 transition-colors shrink-0"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <button
              onClick={logout}
              title="Logout"
              className="w-full flex justify-center py-2 text-slate-400 hover:text-rose-400 transition-colors"
            >
              <LogOut size={20} />
            </button>
          )}
        </div>
      </aside>

      {/* ── Main App Shell ───────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navigation Bar */}
        <header className="h-16 bg-[#0F172A]/80 backdrop-blur-md border-b border-slate-800/80 px-6 flex items-center justify-between shrink-0 z-20">
          {/* Search Bar */}
          <form onSubmit={handleSearchSubmit} className="relative w-72 md:w-96">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search complaints, locations, or keywords..."
              className="w-full bg-[#161F30] border border-slate-700/60 rounded-xl pl-10 pr-4 py-2 text-xs md:text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-purple-500/80 focus:ring-1 focus:ring-purple-500/50 transition-all"
            />
          </form>

          {/* Right Action Icons & Date */}
          <div className="flex items-center gap-3.5">
            {/* Bell Notifications */}
            <button
              className="relative p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors"
              title="3 unread notifications"
            >
              <Bell size={19} />
              <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-purple-600 text-[10px] font-bold text-white rounded-full flex items-center justify-center ring-2 ring-[#0F172A]">
                3
              </span>
            </button>

            {/* Dark / Light Mode Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors"
              title="Toggle Theme"
            >
              {isDarkMode ? <Sun size={19} /> : <Moon size={19} />}
            </button>

            {/* Date Pill */}
            <div className="hidden sm:flex items-center gap-2 bg-[#161F30] border border-slate-700/60 px-3.5 py-1.5 rounded-xl text-xs font-medium text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{formattedDate}</span>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto bg-[#0B0F19] p-5 lg:p-7">
          <div className="max-w-[1600px] mx-auto min-h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
