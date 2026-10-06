import api from './api';
import { API_ENDPOINTS } from '../utils/constants';

const complaintService = {
  submitComplaint: async (formData) => {
    const response = await api.post(API_ENDPOINTS.COMPLAINTS.BASE, formData);
    return response.data;
  },

  getMyComplaints: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.COMPLAINTS.LIST, { params });
    return response.data;
  },

  getComplaintDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.COMPLAINTS.DETAIL(id));
    return response.data;
  },

  getProcessingStatus: async (id) => {
    const response = await api.get(API_ENDPOINTS.COMPLAINTS.PROCESSING_STATUS(id));
    return response.data;
  },

  checkDuplicate: async (data) => {
    const response = await api.post(API_ENDPOINTS.COMPLAINTS.CHECK_DUPLICATE, data);
    return response.data;
  },

  getDuplicates: async (id) => {
    const response = await api.get(API_ENDPOINTS.COMPLAINTS.DUPLICATES(id));
    return response.data;
  },

  getPriority: async (id) => {
    const response = await api.get(API_ENDPOINTS.COMPLAINTS.PRIORITY(id));
    return response.data;
  },
};

export default complaintService;
