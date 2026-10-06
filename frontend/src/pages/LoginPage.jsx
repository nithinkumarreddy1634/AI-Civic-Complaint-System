import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * Authentication pages have been removed per user preference.
 * Redirects directly to the public home portal.
 */
const LoginPage = () => {
  return <Navigate to="/" replace />;
};

export default LoginPage;
