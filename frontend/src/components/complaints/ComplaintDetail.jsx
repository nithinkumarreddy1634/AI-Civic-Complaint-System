import React from 'react';
import {
  MapPin, Calendar, Clock, CheckCircle2, AlertTriangle, AlertCircle,
  ShieldCheck, ShieldAlert, ShieldX, Activity, Layers, Building2,
  Info, XCircle, Eye, Users, Zap, TrendingUp
} from 'lucide-react';
import StatusBadge from '../common/StatusBadge';
import SeverityBadge from '../ai/SeverityBadge';
import PriorityBadge from '../ai/PriorityBadge';
import DetectionOverlay from '../ai/DetectionOverlay';
import { formatDate, getCategoryMeta, formatCoordinates, getImageUrl } from '../../utils/helpers';
import { PROCESSING_STATES } from '../../utils/constants';

// ─── AI Processing Progress Bar ───────────────────────────────────────────────
const ProcessingProgressBar = ({ processingState, progress, message }) => {
  const stateInfo = PROCESSING_STATES[processingState] || { label: processingState, percent: progress || 0 };
  const isFailed = processingState === 'FAILED';
  const isComplete = processingState === 'COMPLETE';

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {isFailed ? (
            <XCircle size={18} className="text-rose-500 shrink-0" />
          ) : isComplete ? (
            <CheckCircle2 size={18} className="text-emerald-500 shrink-0" />
          ) : (
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin shrink-0" />
          )}
          <span className="font-semibold text-sm text-slate-800">
            {isFailed ? 'AI Processing Failed' : isComplete ? 'AI Analysis Complete' : 'AI Processing In Progress'}
          </span>
        </div>
        <span className={`text-xs font-mono font-bold ${isFailed ? 'text-rose-600' : 'text-blue-700'}`}>
          {isFailed ? 'ERROR' : `${stateInfo.percent || progress || 0}%`}
        </span>
      </div>

      {!isFailed && (
        <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
          <div
            className={`h-2 rounded-full transition-all duration-700 ${isComplete ? 'bg-emerald-500' : 'bg-blue-600'}`}
            style={{ width: `${stateInfo.percent || progress || 0}%` }}
          />
        </div>
      )}

      <p className="text-xs text-slate-500">
        {isFailed ? (message || 'Processing failed. Please contact support.') : (message || stateInfo.label)}
      </p>

      {!isComplete && !isFailed && (
        <p className="text-[11px] text-blue-500 mt-1.5">
          This page will automatically update when processing completes.
        </p>
      )}
    </div>
  );
};

// ─── Verification Card ─────────────────────────────────────────────────────────
const VerificationCard = ({ verification }) => {
  if (!verification) return null;

  const statusConfig = {
    VERIFIED: { icon: ShieldCheck, color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200', label: 'Verified' },
    NEEDS_REVIEW: { icon: ShieldAlert, color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200', label: 'Needs Review' },
    REJECTED: { icon: ShieldX, color: 'text-rose-600', bg: 'bg-rose-50 border-rose-200', label: 'Rejected' },
  };
  const cfg = statusConfig[verification.status] || statusConfig.NEEDS_REVIEW;
  const Icon = cfg.icon;

  const pct = (val) => (val != null ? `${(val * 100).toFixed(0)}%` : '—');
  const scorePct = (val) => (val != null ? Math.round(val * 100) : 0);

  const ScoreBar = ({ label, value }) => (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-500">{label}</span>
        <span className="font-mono font-semibold text-slate-800">{pct(value)}</span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-1.5">
        <div
          className="h-1.5 rounded-full bg-blue-500 transition-all"
          style={{ width: `${scorePct(value)}%` }}
        />
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className={`flex items-center gap-3 px-5 py-3.5 border-b ${cfg.bg}`}>
        <Icon size={18} className={cfg.color} />
        <span className="font-semibold text-sm text-slate-800">AI Verification</span>
        <span className={`ml-auto text-xs font-semibold px-2 py-0.5 rounded-full border ${cfg.bg} ${cfg.color}`}>
          {cfg.label}
        </span>
      </div>

      <div className="p-5 space-y-4">
        {/* Detected Class */}
        {verification.detected_class && (
          <div className="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-2.5">
            <span className="text-sm text-slate-500">Detected Class</span>
            <span className="font-semibold text-sm text-slate-900 capitalize">
              {verification.detected_class.replace(/_/g, ' ')}
            </span>
          </div>
        )}

        {/* Score bars */}
        <div className="space-y-3">
          <ScoreBar label="Verification Score" value={verification.score} />
          <ScoreBar label="Detection Confidence" value={verification.confidence} />
          <ScoreBar label="Image Quality" value={verification.image_quality_score} />
          <ScoreBar label="Text–Image Consistency" value={verification.text_consistency_score} />
        </div>

        {/* Explanation tags */}
        {verification.explanation && verification.explanation.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">AI Reasoning</p>
            <div className="flex flex-wrap gap-1.5">
              {verification.explanation.map((e, i) => (
                <span key={i} className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-md px-2 py-0.5">
                  {e}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ─── Severity Card ─────────────────────────────────────────────────────────────
const SeverityCard = ({ severity }) => {
  if (!severity) return null;

  const pct = (val) => Math.round(val ?? 0);

  const RiskBar = ({ label, icon: Icon, value, color }) => (
    <div className="flex items-center gap-3">
      <Icon size={16} className={color} />
      <div className="flex-1">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-slate-600">{label}</span>
          <span className="font-mono font-bold text-slate-800">{pct(value)}/100</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all ${value >= 75 ? 'bg-rose-500' : value >= 50 ? 'bg-amber-500' : 'bg-emerald-500'}`}
            style={{ width: `${pct(value)}%` }}
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b bg-orange-50 border-orange-200">
        <Activity size={18} className="text-orange-600" />
        <span className="font-semibold text-sm text-slate-800">Damage Severity Assessment</span>
        <SeverityBadge level={severity.level} score={severity.score} />
      </div>

      <div className="p-5 space-y-4">
        <div className="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-2.5">
          <span className="text-sm text-slate-500">Overall Severity Score</span>
          <span className="text-2xl font-bold text-slate-900 font-mono">{pct(severity.score)}</span>
        </div>

        <div className="space-y-3.5">
          <RiskBar label="Safety Risk" icon={AlertTriangle} value={severity.safety_risk_score} color="text-rose-500" />
          <RiskBar label="Infrastructure Impact" icon={Layers} value={severity.infrastructure_impact_score} color="text-orange-500" />
          <RiskBar label="Public Impact" icon={Users} value={severity.public_impact_score} color="text-purple-500" />
        </div>

        {severity.evidence && severity.evidence.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Evidence Factors</p>
            <div className="flex flex-wrap gap-1.5">
              {severity.evidence.map((e, i) => (
                <span key={i} className="text-xs bg-orange-50 text-orange-700 border border-orange-200 rounded-md px-2 py-0.5">
                  {e}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ─── Priority Card ─────────────────────────────────────────────────────────────
const PriorityCard = ({ priority }) => {
  if (!priority) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b bg-purple-50 border-purple-200">
        <TrendingUp size={18} className="text-purple-600" />
        <span className="font-semibold text-sm text-slate-800">Intelligent Prioritization</span>
        <PriorityBadge level={priority.level} score={priority.score} />
      </div>

      <div className="p-5 space-y-4">
        {/* Score ring */}
        <div className="flex items-center gap-4 bg-slate-50 rounded-lg px-4 py-3">
          <div className="relative w-14 h-14 shrink-0">
            <svg viewBox="0 0 48 48" className="w-14 h-14 -rotate-90">
              <circle cx="24" cy="24" r="20" fill="none" stroke="#e2e8f0" strokeWidth="5" />
              <circle
                cx="24" cy="24" r="20" fill="none"
                stroke={priority.score >= 75 ? '#f43f5e' : priority.score >= 50 ? '#8b5cf6' : '#3b82f6'}
                strokeWidth="5"
                strokeDasharray={`${(priority.score / 100) * 125.6} 125.6`}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-slate-800">
              {Math.round(priority.score ?? 0)}
            </span>
          </div>
          <div>
            <p className="font-semibold text-slate-800">Priority Score</p>
            <p className="text-xs text-slate-500">Out of 100</p>
            {priority.escalation_boost > 0 && (
              <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                <Zap size={11} /> +{priority.escalation_boost.toFixed(1)} Escalation Boost
              </p>
            )}
          </div>
        </div>

        {/* Contributing factors */}
        {priority.contributing_factors && priority.contributing_factors.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Contributing Factors</p>
            <div className="space-y-1.5">
              {priority.contributing_factors.map((f, i) => (
                <div key={i} className="flex items-center justify-between text-xs bg-slate-50 rounded-md px-3 py-1.5">
                  <span className="text-slate-600 capitalize">{typeof f === 'string' ? f.replace(/_/g, ' ') : f.name?.replace(/_/g, ' ') || 'Factor'}</span>
                  {f.weight != null && <span className="font-mono font-semibold text-purple-700">{(f.weight * 100).toFixed(0)}%</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {priority.explanation && (
          <div className="bg-purple-50 border border-purple-100 rounded-lg px-4 py-3 text-xs text-purple-800 leading-relaxed">
            {priority.explanation}
          </div>
        )}
      </div>
    </div>
  );
};

// ─── Department Card ───────────────────────────────────────────────────────────
const DepartmentCard = ({ department }) => {
  if (!department) return null;

  const dept = typeof department === 'object' ? department : { name: department };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b bg-teal-50 border-teal-200">
        <Building2 size={18} className="text-teal-600" />
        <span className="font-semibold text-sm text-slate-800">Department Assignment</span>
        {dept.confidence != null && (
          <span className="ml-auto text-xs font-mono font-semibold text-teal-700">
            {(dept.confidence * 100).toFixed(0)}% confidence
          </span>
        )}
      </div>

      <div className="p-5">
        <div className="flex items-center gap-4 bg-teal-50 rounded-xl px-4 py-4">
          <div className="w-12 h-12 rounded-xl bg-teal-600 flex items-center justify-center shrink-0">
            <Building2 size={24} className="text-white" />
          </div>
          <div>
            <p className="font-bold text-slate-900 text-base">{dept.department_name || dept.name || 'Unknown'}</p>
            {dept.code && <p className="text-xs text-slate-500 mt-0.5">Code: {dept.code}</p>}
            {dept.reason && <p className="text-xs text-teal-600 mt-0.5">{dept.reason}</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Duplicate Card ────────────────────────────────────────────────────────────
const DuplicateCard = ({ duplicates, isDuplicate }) => {
  if (!duplicates && !isDuplicate) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b bg-amber-50 border-amber-200">
        <AlertCircle size={18} className="text-amber-600" />
        <span className="font-semibold text-sm text-slate-800">Duplicate Detection</span>
        {isDuplicate && (
          <span className="ml-auto text-xs font-semibold text-amber-700 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full">
            Duplicate
          </span>
        )}
      </div>
      <div className="p-5">
        {isDuplicate ? (
          <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-800">
            This complaint was identified as a duplicate. It has been grouped with similar reported issues.
            {duplicates?.group_id && (
              <p className="text-xs mt-1 text-amber-600 font-mono">Group: {duplicates.group_id.substring(0, 8)}…</p>
            )}
            {duplicates?.report_count && (
              <p className="text-xs mt-0.5 text-amber-700">{duplicates.report_count} total reports in this group</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3">
            ✓ No duplicates found. This is a unique complaint.
          </p>
        )}
      </div>
    </div>
  );
};

// ─── Main ComplaintDetail Component ───────────────────────────────────────────
const ComplaintDetail = ({ complaint, processingStatus = null, isAdmin = false }) => {
  if (!complaint) return null;

  const categoryMeta = getCategoryMeta(complaint.category);
  const CategoryIcon = categoryMeta.icon || AlertTriangle;

  const activeProcessing = processingStatus || {
    processing_state: complaint.processing_state,
    progress: complaint.processing_progress,
    message: complaint.processing_message,
  };

  const isProcessing = activeProcessing.processing_state &&
    !['COMPLETE', 'FAILED'].includes(activeProcessing.processing_state);

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[300px]">
          {/* Image with detection overlay */}
          <div className="bg-slate-900 min-h-[260px] lg:min-h-[360px]">
            <DetectionOverlay
              imageSrc={complaint.image_path}
              boundingBox={complaint.verification?.bounding_box}
              imageWidth={complaint.verification?.image_width}
              imageHeight={complaint.verification?.image_height}
              label={complaint.verification?.detected_class}
              confidence={complaint.verification?.confidence}
              className="w-full h-full min-h-[260px] lg:min-h-[360px]"
            />
          </div>

          {/* Details */}
          <div className="p-6 flex flex-col gap-4">
            <div className="flex items-start justify-between">
              <div>
                <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold mb-2 ${categoryMeta.color || 'text-blue-700 bg-blue-50'}`}>
                  <CategoryIcon size={16} />
                  <span>{categoryMeta.label}</span>
                </div>
                <p className="text-xs text-slate-400 font-mono">
                  #{String(complaint.id).substring(0, 8)}
                </p>
              </div>
              <StatusBadge status={complaint.status} />
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Description</p>
              <p className="text-slate-700 text-sm leading-relaxed">{complaint.description}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div className="flex items-start gap-2.5">
                <MapPin size={15} className="text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="block text-xs text-slate-400 mb-0.5">Location</span>
                  <span className="text-slate-700 text-xs">
                    {complaint.address || formatCoordinates(complaint.latitude, complaint.longitude)}
                  </span>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <Calendar size={15} className="text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="block text-xs text-slate-400 mb-0.5">Submitted</span>
                  <span className="text-slate-700 text-xs">{formatDate(complaint.created_at)}</span>
                </div>
              </div>
            </div>

            {/* Quick AI summary chips */}
            {complaint.severity && (
              <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-slate-100">
                <SeverityBadge level={complaint.severity?.level} score={complaint.severity?.score} />
                <PriorityBadge level={complaint.priority_level || complaint.priority?.level} score={complaint.priority?.score} />
                {complaint.is_duplicate && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border bg-amber-100 text-amber-800 border-amber-200">
                    Duplicate
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── AI Processing Progress ── */}
      {isProcessing && (
        <ProcessingProgressBar
          processingState={activeProcessing.processing_state}
          progress={activeProcessing.progress}
          message={activeProcessing.message}
        />
      )}

      {/* ── AI Result Cards ── */}
      {complaint.verification && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <VerificationCard verification={complaint.verification} />
          <SeverityCard severity={complaint.severity} />
        </div>
      )}

      {(complaint.priority || complaint.department) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <PriorityCard priority={complaint.priority} />
          <DepartmentCard department={complaint.department} />
        </div>
      )}

      {/* ── Duplicate Detection ── */}
      <DuplicateCard duplicates={complaint.duplicates} isDuplicate={complaint.is_duplicate} />

      {/* ── Status History (admin) ── */}
      {isAdmin && complaint.status_history && complaint.status_history.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="flex items-center gap-3 px-5 py-3.5 border-b">
            <Clock size={17} className="text-slate-500" />
            <span className="font-semibold text-sm text-slate-800">Status Timeline</span>
          </div>
          <div className="p-5">
            <ol className="relative border-l border-slate-200 space-y-4 pl-4">
              {complaint.status_history.map((h, i) => (
                <li key={i} className="relative">
                  <div className="absolute -left-[21px] top-1 w-3.5 h-3.5 rounded-full bg-blue-600 border-2 border-white shadow-sm" />
                  <div className="text-xs">
                    <div className="flex items-center gap-2 mb-0.5">
                      <StatusBadge status={h.new_status} size="xs" />
                      <span className="text-slate-400">{formatDate(h.changed_at)}</span>
                    </div>
                    {h.remarks && <p className="text-slate-500 mt-0.5 italic">"{h.remarks}"</p>}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplaintDetail;
