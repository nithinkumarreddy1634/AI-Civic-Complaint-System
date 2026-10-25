import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ComplaintForm from '../components/complaints/ComplaintForm';
import complaintService from '../services/complaintService';
import { PlusCircle, ArrowLeft, AlertCircle, CheckCircle2 } from 'lucide-react';

const AdminSubmitComplaintPage = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [submittedId, setSubmittedId] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (formData) => {
    setIsSubmitting(true);
    setError('');

    try {
      const data = new FormData();
      data.append('category', formData.category);
      data.append('description', formData.description);
      if (formData.location?.lat != null) {
        data.append('latitude', formData.location.lat);
      }
      if (formData.location?.lng != null) {
        data.append('longitude', formData.location.lng);
      }
      if (formData.address) {
        data.append('address', formData.address);
      }
      data.append('image', formData.image);

      const response = await complaintService.submitComplaint(data);
      const newId = response.complaint_id || response.id;
      setSubmittedId(newId);
      setSuccess(true);
    } catch (err) {
      console.error('Error submitting complaint from admin:', err);
      const detail = err.response?.data?.detail || err.response?.data?.error?.message || err.response?.data?.message;
      let errorMsg = 'An error occurred while filing the incident. Please verify your input and try again.';
      if (typeof detail === 'string') {
        errorMsg = detail;
      } else if (Array.isArray(detail)) {
        errorMsg = detail.map((d) => (typeof d === 'string' ? d : d.msg || d.message || JSON.stringify(d))).join(', ');
      } else if (err.message) {
        errorMsg = `${err.message}. Please check your connection to the server.`;
      }
      setError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success && submittedId) {
    return (
      <div className="max-w-3xl mx-auto my-8">
        <div className="bg-[#111827] border border-slate-800 p-8 rounded-2xl shadow-2xl text-center space-y-6">
          <div className="w-16 h-16 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 rounded-2xl flex items-center justify-center mx-auto">
            <CheckCircle2 size={36} />
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Incident Successfully Logged & AI Dispatched
            </h2>
            <p className="text-slate-400 text-sm max-w-lg mx-auto">
              The defect has been recorded in the central database. The AI computer vision pipeline is currently running quality verification, damage severity scoring, and duplicate cross-matching.
            </p>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl inline-block max-w-full">
            <span className="text-xs text-slate-400 block mb-1">Incident Reference ID</span>
            <span className="font-mono text-sm sm:text-base font-bold text-purple-400 break-all select-all">
              {submittedId}
            </span>
          </div>

          <div className="flex flex-col sm:flex-row justify-center gap-3 pt-2">
            <Link
              to={`/admin/complaints/${submittedId}`}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-purple-600/30 transition-all text-sm"
            >
              <span>Inspect Live AI Verification</span>
              <span>&rarr;</span>
            </Link>
            <Link
              to="/admin/map"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-slate-700 text-sm transition-all"
            >
              <span>View On Incident Map</span>
            </Link>
            <button
              onClick={() => {
                setSuccess(false);
                setSubmittedId(null);
              }}
              className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold rounded-xl border border-slate-800 text-sm transition-all"
            >
              File Another Report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-[#111827] border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link
              to="/admin/complaints"
              className="text-xs text-slate-400 hover:text-purple-400 flex items-center gap-1 transition-colors"
            >
              <ArrowLeft size={13} />
              <span>Back to Complaints</span>
            </Link>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <PlusCircle size={22} className="text-purple-400" />
            Direct Incident Intake & Verification
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            File civic infrastructure complaints directly into the municipal queue. The AI vision model will automatically inspect image evidence and compute priority scores.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
          <AlertCircle size={18} className="shrink-0 mt-0.5 text-rose-400" />
          <div className="text-xs leading-relaxed">{error}</div>
        </div>
      )}

      {/* Embedded Complaint Filing Form with Real Example Presets */}
      <ComplaintForm onSubmit={handleSubmit} isLoading={isSubmitting} showPresets={true} />
    </div>
  );
};

export default AdminSubmitComplaintPage;
