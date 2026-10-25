import React, { useEffect, useState, useRef } from 'react';
import useAuth from '../../hooks/useAuth';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, roles = [] }) => {
  const { loading, switchRole, isAdmin } = useAuth();
  const [switching, setSwitching] = useState(false);
  const [switchFailed, setSwitchFailed] = useState(false);
  const switchAttemptedRef = useRef(false);

  const needsAdmin = roles.includes('admin');

  useEffect(() => {
    if (needsAdmin && !isAdmin && !switchAttemptedRef.current) {
      switchAttemptedRef.current = true;
      setSwitching(true);
      setSwitchFailed(false);

      switchRole('admin')
        .then((profile) => {
          setSwitching(false);
          if (!profile || profile.role !== 'admin') {
            setSwitchFailed(true);
          }
        })
        .catch((err) => {
          console.error('Failed to switch to admin role:', err);
          setSwitching(false);
          setSwitchFailed(true);
        });
    }
  }, [needsAdmin, isAdmin, switchRole]);

  // While auth context is initializing OR we are actively switching to admin role,
  // do not render children yet (prevents 403 race condition on API calls)
  if (loading || switching || (needsAdmin && !isAdmin && !switchFailed)) {
    return <LoadingSpinner fullScreen />;
  }

  // If admin role is required but switching failed (backend unavailable or wrong credentials)
  if (needsAdmin && !isAdmin && switchFailed) {
    return (
      <div className="min-h-screen bg-[#0B0F19] text-white flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-md w-full bg-[#111827] border border-rose-500/30 rounded-2xl p-8 shadow-2xl">
          <div className="w-12 h-12 bg-rose-500/20 text-rose-400 rounded-xl flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
            !
          </div>
          <h2 className="text-xl font-bold mb-2">Admin Console Connection Issue</h2>
          <p className="text-sm text-slate-400 mb-6">
            Unable to authenticate as admin. Please ensure the backend server is running at <code className="text-purple-400">http://127.0.0.1:8000</code>.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => {
                switchAttemptedRef.current = false;
                setSwitchFailed(false);
                setSwitching(true);
                switchRole('admin')
                  .then((p) => {
                    setSwitching(false);
                    if (!p || p.role !== 'admin') setSwitchFailed(true);
                  })
                  .catch(() => {
                    setSwitching(false);
                    setSwitchFailed(true);
                  });
              }}
              className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-sm font-semibold transition"
            >
              Retry Connection
            </button>
            <a
              href="/"
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-sm font-medium transition"
            >
              Return Home
            </a>
          </div>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;

