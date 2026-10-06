import { useState, useCallback } from 'react';
import complaintService from '../services/complaintService';

const useComplaints = () => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchComplaints = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await complaintService.getMyComplaints(params);
      setComplaints(data.items || data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch complaints');
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback((params) => {
    fetchComplaints(params);
  }, [fetchComplaints]);

  return { complaints, loading, error, fetchComplaints, refresh };
};

export default useComplaints;
