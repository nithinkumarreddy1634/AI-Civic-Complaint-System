import { COMPLAINT_STATUSES, SEVERITY_LEVELS, PRIORITY_LEVELS, COMPLAINT_CATEGORIES } from './constants';

export const formatDate = (dateString) => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch {
    return dateString;
  }
};

export const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://') || imagePath.startsWith('data:')) {
    return imagePath;
  }
  // Remove duplicate leading slashes or upload prefix if doubled
  const normalized = imagePath.replace(/\\/g, '/').replace(/^\/+/, '');
  // If Vite dev server proxies /uploads, or in production against backend
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  if (baseUrl) {
    const origin = baseUrl.replace(/\/api\/?$/, '');
    return `${origin}/${normalized}`;
  }
  return `/${normalized}`;
};

export const formatStatus = (status) => {
  if (!status) return 'Unknown';
  return COMPLAINT_STATUSES[status]?.label || status.replace(/_/g, ' ');
};

export const getStatusColor = (status) => {
  if (!status) return 'bg-slate-100 text-slate-800 border-slate-200';
  return COMPLAINT_STATUSES[status]?.color || 'bg-slate-100 text-slate-800 border-slate-200';
};

export const getSeverityColor = (level) => {
  if (!level) return 'bg-slate-100 text-slate-800 border-slate-200';
  const upper = level.toUpperCase();
  return SEVERITY_LEVELS[upper]?.color || 'bg-slate-100 text-slate-800 border-slate-200';
};

export const getPriorityColor = (level) => {
  if (!level) return 'bg-slate-100 text-slate-800 border-slate-200';
  const upper = level.toUpperCase();
  return PRIORITY_LEVELS[upper]?.color || 'bg-slate-100 text-slate-800 border-slate-200';
};

export const getCategoryMeta = (categoryValue) => {
  return COMPLAINT_CATEGORIES.find((c) => c.value === categoryValue) || {
    value: categoryValue,
    label: categoryValue?.replace(/_/g, ' ') || 'General Issue',
    color: 'text-slate-600 bg-slate-50',
  };
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text || '';
  return text.substring(0, maxLength) + '...';
};

export const formatCoordinates = (lat, lng) => {
  if (lat == null || lng == null) return 'Not available';
  return `${Number(lat).toFixed(5)}°, ${Number(lng).toFixed(5)}°`;
};
