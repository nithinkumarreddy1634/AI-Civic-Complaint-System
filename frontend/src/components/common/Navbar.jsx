import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Menu, X, Shield, PlusCircle, LayoutDashboard, UserCheck, ShieldAlert, Sparkles } from 'lucide-react';
import useAuth from '../../hooks/useAuth';

const Navbar = () => {
  const { user, activeRole, switchRole, isAdmin } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleRoleToggle = async (newRole) => {
    await switchRole(newRole);
    if (newRole === 'admin' && !location.pathname.startsWith('/admin')) {
      navigate('/admin');
    } else if (newRole === 'citizen' && location.pathname.startsWith('/admin')) {
      navigate('/complaints');
    }
  };

  return (
    <nav className="bg-[#0F172A]/90 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-50">
      <div className="container mx-auto px-4 lg:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-600/30">
              <Shield className="text-white" size={20} />
            </div>
            <div>
              <span className="font-bold text-lg text-white tracking-wide block leading-tight">CivicPulse</span>
              <span className="text-[10px] text-purple-400 font-semibold uppercase tracking-wider block">AI Infrastructure</span>
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6 text-sm">
            <Link to="/" className="text-slate-300 hover:text-white font-medium transition-colors">
              Home
            </Link>

            <Link
              to="/complaints/new"
              className="flex items-center gap-1.5 text-purple-400 hover:text-purple-300 font-medium transition-colors"
            >
              <PlusCircle size={16} />
              <span>Submit Complaint</span>
            </Link>

            <Link to="/complaints" className="text-slate-300 hover:text-white font-medium transition-colors">
              My Complaints
            </Link>

            <Link
              to="/admin"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600/30 font-medium transition-colors"
            >
              <LayoutDashboard size={15} />
              <span>Admin Console</span>
            </Link>

            {/* Seamless Role Switcher (Zero Auth Page) */}
            <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
              <div className="bg-slate-900/90 border border-slate-800 p-1 rounded-xl flex items-center gap-1 shadow-inner">
                <button
                  type="button"
                  onClick={() => handleRoleToggle('citizen')}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                    activeRole !== 'admin'
                      ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="Switch to Citizen View"
                >
                  <UserCheck size={13} />
                  <span>Citizen</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleRoleToggle('admin')}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                    activeRole === 'admin'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title="Switch to Admin View"
                >
                  <ShieldAlert size={13} />
                  <span>Admin</span>
                </button>
              </div>

              {/* Persona Tag */}
              <div className="text-right hidden lg:block pl-1">
                <span className="text-xs font-medium text-slate-200 block leading-tight">
                  {user?.name || (activeRole === 'admin' ? 'Admin User' : 'Citizen')}
                </span>
                <span className="text-[10px] text-emerald-400 font-semibold tracking-wider uppercase block">
                  ● Active
                </span>
              </div>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-slate-400 hover:text-white p-1 rounded-lg"
            >
              {isOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-[#0F172A] border-b border-slate-800 px-4 py-3 space-y-2">
          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800"
          >
            Home
          </Link>
          <Link
            to="/complaints/new"
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm text-purple-400 hover:bg-slate-800 font-medium"
          >
            Submit Complaint
          </Link>
          <Link
            to="/complaints"
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800"
          >
            My Complaints
          </Link>
          <Link
            to="/admin"
            onClick={() => {
              handleRoleToggle('admin');
              setIsOpen(false);
            }}
            className="block px-3 py-2 rounded-lg text-sm text-purple-300 hover:bg-slate-800 font-semibold"
          >
            Admin Dashboard
          </Link>

          {/* Mobile Role Switcher */}
          <div className="pt-2 border-t border-slate-800/80 flex gap-2">
            <button
              type="button"
              onClick={() => {
                handleRoleToggle('citizen');
                setIsOpen(false);
              }}
              className={`flex-1 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 ${
                activeRole !== 'admin'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              <UserCheck size={14} />
              <span>Citizen View</span>
            </button>
            <button
              type="button"
              onClick={() => {
                handleRoleToggle('admin');
                setIsOpen(false);
              }}
              className={`flex-1 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 ${
                activeRole === 'admin'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              <ShieldAlert size={14} />
              <span>Admin View</span>
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
