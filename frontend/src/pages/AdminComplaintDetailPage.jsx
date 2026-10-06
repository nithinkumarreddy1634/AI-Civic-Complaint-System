import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Building2, RefreshCw, ChevronDown } from 'lucide-react';
import adminService from '../services/adminService';
import ComplaintDetail from '../components/complaints/ComplaintDetail';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { COMPLAINT_STATUSES } from '../utils/constants';

// ── Department Assignment Form ────────────────────────────────────────────────
const DepartmentAssignForm = ({ complaintId, currentDept, onSuccess }) => {
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // We derive departments from /api/admin/dashboard's by_department if available
  // Alternatively, we allow free text for department_id
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDept.trim()) {
      setError('Please enter a department ID or name.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await adminService.assignComplaint(complaintId, { department_id: selectedDept, notes });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to assign department.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b bg-teal-50 border-teal-200">
        <Building2 size={18} className="text-teal-600" />
        <span className="font-semibold text-sm text-slate-800">Assign Department</span>
      </div>
      <form onSubmit={handleSubmit} className="p-5 space-y-3">
        {error && (
          <p className="text-xs text-rose-600 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">{error}</p>
        )}
        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">Department ID</label>
          <input
            type="text"
            value={selectedDept}
            onChange={(e) => setSelectedDept(e.target.value)}
            placeholder="Enter department UUID or name"
            className="w-full text-sm bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <p className="text-[11px] text-slate-400 mt-1">Use the department UUID from the system.</p>
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">Notes (Optional)</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows="2"
            placeholder="Assignment notes or instructions..."
            className="w-full text-sm bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-teal-600 text-white rounded-lg text-sm font-semibold hover:bg-teal-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Assigning...' : 'Assign to Department'}
        </button>
      </form>
    </div>
  );
};

// ── Status Update Form ────────────────────────────────────────────────────────
const StatusUpdateForm = ({ complaintId, currentStatus, onSuccess }) => {
  const VALID_TRANSITIONS = {
    SUBMITTED: ['AI_PROCESSING', 'REJECTED'],
    AI_PROCESSING: ['VERIFIED', 'NEEDS_REVIEW', 'REJECTED'],
    VERIFIED: ['PRIORITIZED', 'REJECTED'],
    NEEDS_REVIEW: ['VERIFIED', 'REJECTED'],
    PRIORITIZED: ['ASSIGNED'],
    ASSIGNED: ['IN_PROGRESS'],
    IN_PROGRESS: ['RESOLVED', 'NEEDS_REVIEW'],
    RESOLVED: ['CLOSED'],
    REJECTED: [],
    CLOSED: [],
  };

  const [newStatus, setNewStatus] = useState('');
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const allowed = VALID_TRANSITIONS[currentStatus] || [];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newStatus) { setError('Select a new status.'); return; }
    setLoading(true);
    setError('');
    try {
      await adminService.updateStatus(complaintId, { new_status: newStatus, remarks });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Status update failed.');
    } finally {
      setLoading(false);
    }
  };

  if (allowed.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 text-sm text-slate-500">
        No further status transitions available for <strong>{currentStatus}</strong>.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b bg-indigo-50 border-indigo-200">
        <ChevronDown size={18} className="text-indigo-600" />
        <span className="font-semibold text-sm text-slate-800">Update Status</span>
        <span className="ml-auto text-xs font-mono text-slate-500">Current: {currentStatus}</span>
      </div>
      <form onSubmit={handleSubmit} className="p-5 space-y-3">
        {error && (
          <p className="text-xs text-rose-600 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">{error}</p>
        )}
        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">New Status</label>
          <select
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="w-full text-sm bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">Select status...</option>
            {allowed.map((s) => (
              <option key={s} value={s}>{COMPLAINT_STATUSES[s]?.label || s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-500 mb-1">Remarks (Optional)</label>
          <textarea
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            rows="2"
            placeholder="Add transition notes..."
            className="w-full text-sm bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Updating...' : 'Update Status'}
        </button>
      </form>
    </div>
  );
};

// ── Main Page ─────────────────────────────────────────────────────────────────
const AdminComplaintDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchComplaint = useCallback(async () => {
    try {
      const data = await adminService.getComplaintDetail(id);
      setComplaint(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load complaint.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchComplaint(); }, [fetchComplaint]);

  if (loading) return <LoadingSpinner fullScreen />;

  if (error) {
    return (
      <div className="text-center py-16">
        <div className="text-rose-600 bg-rose-50 border border-rose-200 rounded-xl p-5 inline-block mb-4">
          {error}
        </div>
        <br />
        <button onClick={() => navigate(-1)} className="text-blue-600 hover:underline text-sm">← Back</button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors text-sm font-medium"
        >
          <ArrowLeft size={16} />
          Back to Complaints
        </button>
        <button
          onClick={fetchComplaint}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-blue-600"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main detail */}
        <div className="xl:col-span-2">
          <ComplaintDetail complaint={complaint} isAdmin={true} />
        </div>

        {/* Admin action panel */}
        <div className="space-y-5">
          <StatusUpdateForm
            complaintId={id}
            currentStatus={complaint?.status}
            onSuccess={fetchComplaint}
          />
          <DepartmentAssignForm
            complaintId={id}
            currentDept={complaint?.department}
            onSuccess={fetchComplaint}
          />
        </div>
      </div>
    </div>
  );
};

export default AdminComplaintDetailPage;
