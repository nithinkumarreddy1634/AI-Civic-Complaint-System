import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, Shield, PlusCircle, LayoutDashboard, AlertCircle, LogOut } from 'lucide-react';
import useAuth from '../../hooks/useAuth';

const Navbar = () => {
  const { user, logout, isAdmin, isCitizen } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
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

            {isCitizen && (
              <>
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
              </>
            )}

            {isAdmin && (
              <Link
                to="/admin"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600/30 font-medium transition-colors"
              >
                <LayoutDashboard size={15} />
                <span>Admin Console</span>
              </Link>
            )}

            {user ? (
              <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
                <div className="text-right">
                  <span className="text-xs font-semibold text-slate-200 block">{user.name}</span>
                  <span className="text-[10px] text-slate-400 block uppercase tracking-wider">{user.role}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 rounded-lg transition-colors"
                  title="Logout"
                >
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="text-slate-300 hover:text-white font-medium px-3 py-1.5 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-500 rounded-xl shadow-lg shadow-purple-600/30 transition-all"
                >
                  Register
                </Link>
              </div>
            )}
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
          {isCitizen && (
            <>
              <Link
                to="/complaints/new"
                onClick={() => setIsOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm text-purple-400 hover:bg-slate-800"
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
            </>
          )}
          {isAdmin && (
            <Link
              to="/admin"
              onClick={() => setIsOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm text-purple-300 hover:bg-slate-800 font-semibold"
            >
              Admin Dashboard
            </Link>
          )}
          {user ? (
            <button
              onClick={handleLogout}
              className="block w-full text-left px-3 py-2 rounded-lg text-sm text-rose-400 hover:bg-slate-800"
            >
              Logout ({user.name})
            </button>
          ) : (
            <div className="pt-2 flex gap-2">
              <Link
                to="/login"
                onClick={() => setIsOpen(false)}
                className="flex-1 text-center py-2 rounded-lg bg-slate-800 text-sm text-slate-200"
              >
                Login
              </Link>
              <Link
                to="/register"
                onClick={() => setIsOpen(false)}
                className="flex-1 text-center py-2 rounded-lg bg-purple-600 text-sm text-white font-semibold"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
