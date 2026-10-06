import {
  AlertTriangle,
  Trash2,
  Droplets,
  Zap,
  TreePine,
  CircleDot,
  Footprints,
  Construction,
  ShieldAlert,
  HelpCircle,
} from 'lucide-react';

export const COMPLAINT_CATEGORIES = [
  { value: 'pothole', label: 'Pothole', icon: AlertTriangle, color: 'text-amber-600 bg-amber-50' },
  { value: 'garbage_accumulation', label: 'Garbage Accumulation', icon: Trash2, color: 'text-emerald-600 bg-emerald-50' },
  { value: 'open_manhole', label: 'Open Manhole', icon: CircleDot, color: 'text-red-600 bg-red-50' },
  { value: 'damaged_road', label: 'Damaged Road', icon: Construction, color: 'text-orange-600 bg-orange-50' },
  { value: 'broken_streetlight', label: 'Broken Streetlight', icon: Zap, color: 'text-yellow-600 bg-yellow-50' },
  { value: 'water_leakage', label: 'Water Leakage', icon: Droplets, color: 'text-cyan-600 bg-cyan-50' },
  { value: 'damaged_sidewalk', label: 'Damaged Sidewalk', icon: Footprints, color: 'text-teal-600 bg-teal-50' },
  { value: 'fallen_tree', label: 'Fallen Tree', icon: TreePine, color: 'text-green-600 bg-green-50' },
  { value: 'illegal_dumping', label: 'Illegal Dumping', icon: ShieldAlert, color: 'text-purple-600 bg-purple-50' },
  { value: 'other', label: 'Other Civic Issue', icon: HelpCircle, color: 'text-slate-600 bg-slate-50' },
];

export const COMPLAINT_STATUSES = {
  SUBMITTED: { label: 'Submitted', color: 'bg-slate-100 text-slate-800 border-slate-200' },
  AI_PROCESSING: { label: 'AI Processing', color: 'bg-amber-100 text-amber-800 border-amber-200' },
  VERIFIED: { label: 'Verified', color: 'bg-blue-100 text-blue-800 border-blue-200' },
  NEEDS_REVIEW: { label: 'Needs Review', color: 'bg-orange-100 text-orange-800 border-orange-200' },
  REJECTED: { label: 'Rejected', color: 'bg-rose-100 text-rose-800 border-rose-200' },
  PRIORITIZED: { label: 'Prioritized', color: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
  ASSIGNED: { label: 'Assigned', color: 'bg-purple-100 text-purple-800 border-purple-200' },
  IN_PROGRESS: { label: 'In Progress', color: 'bg-sky-100 text-sky-800 border-sky-200' },
  RESOLVED: { label: 'Resolved', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
  CLOSED: { label: 'Closed', color: 'bg-gray-100 text-gray-800 border-gray-200' },
};

export const SEVERITY_LEVELS = {
  LOW: { label: 'Low', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
  MEDIUM: { label: 'Medium', color: 'bg-amber-100 text-amber-800 border-amber-200' },
  HIGH: { label: 'High', color: 'bg-orange-100 text-orange-800 border-orange-200' },
  CRITICAL: { label: 'Critical', color: 'bg-rose-100 text-rose-800 border-rose-200' },
};

export const PRIORITY_LEVELS = {
  LOW: { label: 'Low', color: 'bg-slate-100 text-slate-800 border-slate-200' },
  MEDIUM: { label: 'Medium', color: 'bg-blue-100 text-blue-800 border-blue-200' },
  HIGH: { label: 'High', color: 'bg-purple-100 text-purple-800 border-purple-200' },
  URGENT: { label: 'Urgent', color: 'bg-rose-100 text-rose-800 border-rose-200' },
};

export const PROCESSING_STATES = {
  PENDING: { label: 'Queued', step: 1, percent: 10 },
  PROCESSING: { label: 'Analyzing Image', step: 2, percent: 25 },
  VERIFICATION_COMPLETE: { label: 'Verification Done', step: 3, percent: 45 },
  SEVERITY_COMPLETE: { label: 'Severity Assessed', step: 4, percent: 65 },
  DUPLICATE_CHECK_COMPLETE: { label: 'Duplicate Checked', step: 5, percent: 80 },
  PRIORITY_COMPLETE: { label: 'Prioritized', step: 6, percent: 90 },
  DEPARTMENT_RECOMMENDED: { label: 'Department Recommended', step: 7, percent: 95 },
  COMPLETE: { label: 'Completed', step: 8, percent: 100 },
  FAILED: { label: 'Failed', step: 0, percent: 100 },
};

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  COMPLAINTS: {
    BASE: '/complaints',
    LIST: '/complaints',
    DETAIL: (id) => `/complaints/${id}`,
    PROCESSING_STATUS: (id) => `/complaints/${id}/processing-status`,
    CHECK_DUPLICATE: '/complaints/check-duplicate',
    DUPLICATES: (id) => `/complaints/${id}/duplicates`,
    PRIORITY: (id) => `/complaints/${id}/priority`,
  },
  ADMIN: {
    DASHBOARD: '/admin/dashboard',
    COMPLAINTS: '/admin/complaints',
    DETAIL: (id) => `/admin/complaints/${id}`,
    ASSIGN: (id) => `/admin/complaints/${id}/assign`,
    STATUS: (id) => `/admin/complaints/${id}/status`,
    ANALYTICS: '/admin/analytics',
    HOTSPOTS: '/admin/hotspots',
  },
};
