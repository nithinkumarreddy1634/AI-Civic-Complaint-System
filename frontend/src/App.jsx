import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import AdminLayout from './layouts/AdminLayout';
import ProtectedRoute from './components/common/ProtectedRoute';

// Public / Citizen Pages
import HomePage from './pages/HomePage';
import SubmitComplaintPage from './pages/SubmitComplaintPage';
import MyComplaintsPage from './pages/MyComplaintsPage';
import ComplaintDetailPage from './pages/ComplaintDetailPage';
import NotFoundPage from './pages/NotFoundPage';

// Admin Pages
import AdminDashboardPage from './pages/AdminDashboardPage';
import AdminComplaintsPage from './pages/AdminComplaintsPage';
import AdminComplaintDetailPage from './pages/AdminComplaintDetailPage';
import AdminMapPage from './pages/AdminMapPage';
import AdminAnalyticsPage from './pages/AdminAnalyticsPage';

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* ── Public / Citizen Routes (inside MainLayout) ─────────────── */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          
          {/* Legacy auth route redirects */}
          <Route path="login" element={<Navigate to="/" replace />} />
          <Route path="register" element={<Navigate to="/complaints/new" replace />} />

          {/* Citizen Routes */}
          <Route
            path="complaints"
            element={
              <ProtectedRoute roles={['citizen']}>
                <MyComplaintsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="complaints/new"
            element={
              <ProtectedRoute roles={['citizen']}>
                <SubmitComplaintPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="complaints/:id"
            element={
              <ProtectedRoute roles={['citizen']}>
                <ComplaintDetailPage />
              </ProtectedRoute>
            }
          />
        </Route>

        {/* ── Admin Routes (inside AdminLayout) ───────────────────────── */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<AdminDashboardPage />} />
          <Route path="complaints" element={<AdminComplaintsPage />} />
          <Route path="complaints/:id" element={<AdminComplaintDetailPage />} />
          <Route path="map" element={<AdminMapPage />} />
          <Route path="analytics" element={<AdminAnalyticsPage />} />
        </Route>

        {/* ── 404 ─────────────────────────────────────────────────────── */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
