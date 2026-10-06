import React, { useEffect } from 'react';
import useAuth from '../../hooks/useAuth';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children, roles = [] }) => {
  const { loading, switchRole, activeRole } = useAuth();

  useEffect(() => {
    // If the route specifically needs admin role and active role isn't admin, switch to admin automatically
    if (roles.includes('admin') && activeRole !== 'admin') {
      switchRole('admin');
    }
  }, [roles, activeRole, switchRole]);

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return children;
};

export default ProtectedRoute;
