import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import complaintService from '../services/complaintService';
import ComplaintCard from '../components/complaints/ComplaintCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Plus, Filter, Sparkles } from 'lucide-react';

const STATUS_TABS = [
  { id: 'ALL', label: 'All' },
  { id: 'AI_PROCESSING', label: 'Processing' },
  { id: 'VERIFIED', label: 'Verified' },
  { id: 'NEEDS_REVIEW', label: 'Needs Review' },
  { id: 'ASSIGNED', label: 'Assigned' },
  { id: 'IN_PROGRESS', label: 'In Progress' },
  { id: 'RESOLVED', label: 'Resolved' },
  { id: 'REJECTED', label: 'Rejected' },
];

const MyComplaintsPage = () => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('ALL');

  useEffect(() => {
    const fetchComplaints = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await complaintService.getMyComplaints({ limit: 50 });
        setComplaints(Array.isArray(data) ? data : data.items || []);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch complaints');
      } finally {
        setLoading(false);
      }
    };
    fetchComplaints();
  }, []);

  const filteredComplaints = activeTab === 'ALL'
    ? complaints
    : complaints.filter((c) => c.status === activeTab);

  // Compute per-tab counts
  const counts = STATUS_TABS.reduce((acc, tab) => {
    acc[tab.id] = tab.id === 'ALL'
      ? complaints.length
      : complaints.filter((c) => c.status === tab.id).length;
    return acc;
  }, {});

  if (loading) return <LoadingSpinner fullScreen />;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-semibold mb-2">
            <Sparkles size={12} className="text-purple-400" />
            <span>Citizen Incident Tracking</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            My Submitted Complaints
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Monitor real-time AI verification results, severity rankings, and municipal resolution milestones.
          </p>
        </div>
        <Link
          to="/complaints/new"
          className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-5 py-2.5 rounded-xl shadow-lg shadow-purple-600/30 transition-all font-semibold text-sm shrink-0"
        >
          <Plus size={18} />
          Report Issue
        </Link>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl mb-6 text-sm">
          {error}
        </div>
      )}

      {/* Status Tabs */}
      <div className="border-b border-slate-800 mb-6 overflow-x-auto">
        <div className="flex gap-2 min-w-max pb-1">
          {STATUS_TABS.map((tab) =>
            counts[tab.id] > 0 || tab.id === 'ALL' ? (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 pb-2.5 pt-1.5 px-3.5 text-xs sm:text-sm font-semibold rounded-t-xl transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-b-2 border-purple-500 text-purple-400 bg-purple-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {tab.label}
                {counts[tab.id] > 0 && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                    activeTab === tab.id ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {counts[tab.id]}
                  </span>
                )}
              </button>
            ) : null
          )}
        </div>
      </div>

      {filteredComplaints.length === 0 ? (
        <div className="text-center py-20 bg-[#111827]/60 rounded-2xl border border-slate-800/80">
          <div className="w-16 h-16 bg-slate-800/80 rounded-2xl flex items-center justify-center mx-auto mb-4 text-slate-400">
            <Filter size={28} />
          </div>
          <p className="text-slate-200 font-semibold text-lg mb-1">
            {activeTab === 'ALL' ? 'No complaints yet' : `No ${activeTab.toLowerCase().replace(/_/g, ' ')} complaints`}
          </p>
          <p className="text-slate-400 text-sm mb-6 max-w-sm mx-auto">
            {activeTab === 'ALL'
              ? 'Submit your first civic defect photo and GPS to initiate AI-powered processing.'
              : 'Try selecting a different status filter tab above.'}
          </p>
          {activeTab === 'ALL' && (
            <Link
              to="/complaints/new"
              className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-purple-600/30 transition-all"
            >
              <Plus size={16} />
              Report an Issue
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredComplaints.map((complaint) => (
            <ComplaintCard key={complaint.id} complaint={complaint} />
          ))}
        </div>
      )}
    </div>
  );
};

export default MyComplaintsPage;
