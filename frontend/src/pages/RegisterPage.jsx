import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * Authentication pages have been removed per user preference.
 * Redirects directly to the complaint submission page.
 */
const RegisterPage = () => {
  return <Navigate to="/complaints/new" replace />;
};

export default RegisterPage;
