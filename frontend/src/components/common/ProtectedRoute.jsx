import React, { useEffect, useState, useRef } from 'react';
import useAuth from '../../hooks/useAuth';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, roles = [] }) => {
  const { loading, switchRole, isAdmin, activeRole } = useAuth();
  const [switching, setSwitching] = useState(false);
  const switchAttemptedRef = useRef(false);

  const needsAdmin = roles.includes('admin');
  const isAuthorized = !needsAdmin || isAdmin || activeRole === 'admin';

  useEffect(() => {
    if (needsAdmin && !isAuthorized && !switchAttemptedRef.current) {
      switchAttemptedRef.current = true;
      setSwitching(true);

      switchRole('admin')
        .finally(() => {
          setSwitching(false);
        });
    }
  }, [needsAdmin, isAuthorized, switchRole]);

  // If already authorized, render immediately (no spinner delay)
  if (isAuthorized) {
    return children;
  }

  // While switching role
  if (loading || switching) {
    return <LoadingSpinner fullScreen />;
  }

  return children;
};

export default ProtectedRoute;
