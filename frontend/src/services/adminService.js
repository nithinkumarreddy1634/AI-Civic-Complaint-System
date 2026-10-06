import api from './api';
import { API_ENDPOINTS } from '../utils/constants';

const adminService = {
  getDashboard: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN.DASHBOARD);
    return response.data;
  },

  getAllComplaints: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.ADMIN.COMPLAINTS, { params });
    return response.data;
  },

  getComplaintDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.ADMIN.DETAIL(id));
    return response.data;
  },

  assignComplaint: async (id, data) => {
    const response = await api.put(API_ENDPOINTS.ADMIN.ASSIGN(id), data);
    return response.data;
  },

  updateStatus: async (id, { new_status, remarks }) => {
    const response = await api.put(API_ENDPOINTS.ADMIN.STATUS(id), null, {
      params: {
        new_status,
        remarks: remarks || undefined,
      },
    });
    return response.data;
  },

  getAnalytics: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN.ANALYTICS);
    return response.data;
  },

  getHotspots: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN.HOTSPOTS);
    return response.data;
  },
};

export default adminService;
