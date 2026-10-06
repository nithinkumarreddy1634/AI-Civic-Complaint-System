import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import adminService from '../services/adminService';
import ComplaintTable from '../components/admin/ComplaintTable';
import ComplaintFilters from '../components/admin/ComplaintFilters';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const AdminComplaintsPage = () => {
  const [complaints, setComplaints] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ sort_by: 'priority_desc' });
  const [page, setPage] = useState(1);
  const limit = 20;
  const navigate = useNavigate();

  const fetchComplaints = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminService.getAllComplaints({ ...filters, page, limit });
      const items = data.items || data;
      setComplaints(Array.isArray(items) ? items : []);
      setTotal(data.total || items.length);
    } catch (error) {
      console.error('Failed to load complaints:', error);
      setComplaints([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchComplaints();
  }, [fetchComplaints]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(1); // reset to first page when filters change
  };

  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div>
      <div className="mb-5">
        <h1 className="text-2xl font-bold text-slate-900">Manage Complaints</h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Review, assign, and update status for all reported issues
        </p>
      </div>

      <ComplaintFilters filters={filters} onFilterChange={handleFilterChange} />

      {loading ? (
        <div className="py-16"><LoadingSpinner /></div>
      ) : (
        <>
          <ComplaintTable
            complaints={complaints}
            onRowClick={(id) => navigate(`/admin/complaints/${id}`)}
          />

          {/* Pagination */}
          <div className="mt-5 flex items-center justify-between text-sm text-slate-500">
            <span>
              Showing {((page - 1) * limit) + 1}–{Math.min(page * limit, total)} of {total} complaints
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg font-semibold text-sm">
                {page}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminComplaintsPage;
