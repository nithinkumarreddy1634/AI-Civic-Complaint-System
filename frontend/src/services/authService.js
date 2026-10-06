import api from './api';
import { API_ENDPOINTS } from '../utils/constants';

const authService = {
  register: async (name, email, password) => {
    const response = await api.post(API_ENDPOINTS.AUTH.REGISTER, { name, email, password });
    return response.data;
  },
  login: async (email, password) => {
    const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, { email, password });
    return response.data;
  },
  getProfile: async () => {
    const response = await api.get(API_ENDPOINTS.AUTH.ME);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  }
};

export default authService;
