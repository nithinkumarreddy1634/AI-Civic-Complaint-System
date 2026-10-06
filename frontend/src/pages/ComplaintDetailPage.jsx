import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import complaintService from '../services/complaintService';
import adminService from '../services/adminService';
import useAuth from '../hooks/useAuth';
import useProcessingStatus from '../hooks/useProcessingStatus';
import ComplaintDetail from '../components/complaints/ComplaintDetail';
import LoadingSpinner from '../components/common/LoadingSpinner';

const ComplaintDetailPage = () => {
  const { id } = useParams();
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDetail = useCallback(async () => {
    try {
      const data = isAdmin
        ? await adminService.getComplaintDetail(id)
        : await complaintService.getComplaintDetail(id);
      setComplaint(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load complaint details.');
    } finally {
      setLoading(false);
    }
  }, [id, isAdmin]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  // Poll for processing status when complaint is in processing state
  const needsPolling = complaint &&
    complaint.processing_state &&
    !['COMPLETE', 'FAILED'].includes(complaint.processing_state);

  const { processing_state, progress, message, isComplete } = useProcessingStatus(
    needsPolling ? id : null,
    complaint,
    (completedData) => {
      // Refresh the full complaint when AI pipeline completes
      setTimeout(() => fetchDetail(), 1000);
    }
  );

  if (loading) return <LoadingSpinner fullScreen />;

  if (error) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16 px-4">
        <div className="bg-rose-50 border border-rose-200 text-rose-700 p-5 rounded-xl mb-6 inline-block">
          {error}
        </div>
        <div>
          <button
            onClick={() => navigate(-1)}
            className="text-blue-600 hover:underline font-medium text-sm"
          >
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  const activeProcessingStatus = needsPolling
    ? { processing_state, progress, message }
    : null;

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors text-sm font-medium"
        >
          <ArrowLeft size={16} />
          Back
        </button>
        <button
          onClick={fetchDetail}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-blue-600 transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <ComplaintDetail
        complaint={complaint}
        processingStatus={activeProcessingStatus}
        isAdmin={isAdmin}
      />
    </div>
  );
};

export default ComplaintDetailPage;
