import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ComplaintForm from '../components/complaints/ComplaintForm';
import complaintService from '../services/complaintService';
import { CheckCircle2, ArrowRight, AlertCircle, Sparkles } from 'lucide-react';

const SubmitComplaintPage = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [submittedId, setSubmittedId] = useState(null);
  const [error, setError] = useState('');
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
      console.error('Error submitting complaint:', err);
      const detail = err.response?.data?.detail || err.response?.data?.error?.message || err.response?.data?.message;
      let errorMsg = 'An error occurred while submitting your complaint. Please verify your input and try again.';
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

  if (success) {
    return (
      <div className="max-w-2xl mx-auto my-12 px-4">
        <div className="bg-[#111827]/90 p-8 sm:p-10 rounded-2xl shadow-2xl border border-slate-800 text-center">
          <div className="w-16 h-16 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <CheckCircle2 size={36} />
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
            Complaint Submitted!
          </h2>
          <p className="text-slate-400 mb-6 text-sm">
            Your complaint has been queued for real-time AI verification and prioritization.
          </p>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 mb-8 inline-block max-w-full">
            <span className="text-xs text-slate-400 block mb-1">Incident Reference Number</span>
            <span className="font-mono text-sm sm:text-base font-bold text-purple-400 break-all select-all">
              {submittedId}
            </span>
          </div>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to={`/complaints/${submittedId}`}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-purple-600/30 transition-all text-sm"
            >
              <span>Track AI Verification</span>
              <ArrowRight size={16} />
            </Link>
            <button
              onClick={() => {
                setSuccess(false);
                setSubmittedId(null);
              }}
              className="px-6 py-3 bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 font-semibold rounded-xl border border-slate-700 text-sm transition-all"
            >
              Submit Another Report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-4">
      <div className="mb-6 space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-semibold">
          <Sparkles size={12} className="text-purple-400" />
          <span>Citizen Reporting Portal</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Report Civic Infrastructure Issue
        </h1>
        <p className="text-slate-400 text-sm">
          Submit photos and GPS coordinates. The AI verification engine will audit image validity, detect defects, evaluate safety severity, and route to the responsible department.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
          <AlertCircle size={18} className="shrink-0 mt-0.5 text-rose-400" />
          <div className="text-xs leading-relaxed">{error}</div>
        </div>
      )}

      <ComplaintForm onSubmit={handleSubmit} isLoading={isSubmitting} />
    </div>
  );
};

export default SubmitComplaintPage;
