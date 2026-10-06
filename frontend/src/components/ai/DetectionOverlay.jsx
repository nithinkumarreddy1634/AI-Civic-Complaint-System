import React, { useState } from 'react';
import { Eye, EyeOff, Sparkles } from 'lucide-react';
import { getImageUrl } from '../../utils/helpers';

const DetectionOverlay = ({
  imageSrc,
  boundingBox = null,
  imageWidth = null,
  imageHeight = null,
  label = null,
  confidence = null,
  className = '',
}) => {
  const [showOverlay, setShowOverlay] = useState(true);

  if (!imageSrc) {
    return (
      <div className={`flex items-center justify-center bg-slate-100 text-slate-400 ${className}`}>
        No image available
      </div>
    );
  }

  const resolvedSrc = getImageUrl(imageSrc);

  // Extract raw coordinates
  let box = null;
  if (boundingBox) {
    if (Array.isArray(boundingBox)) {
      box = boundingBox;
    } else if (boundingBox.bbox && Array.isArray(boundingBox.bbox)) {
      box = boundingBox.bbox;
    } else if (typeof boundingBox === 'object' && boundingBox.x != null) {
      // Already { x, y, width, height } in percent
      return (
        <div className={`relative overflow-hidden rounded-xl bg-slate-900 ${className}`}>
          <img src={resolvedSrc} alt="Complaint Evidence" className="w-full h-full object-cover" />
          {showOverlay && (
            <div
              className="absolute border-2 border-rose-500 bg-rose-500/20 shadow-[0_0_12px_rgba(244,63,94,0.5)] transition-all pointer-events-none"
              style={{
                top: `${boundingBox.y}%`,
                left: `${boundingBox.x}%`,
                width: `${boundingBox.width}%`,
                height: `${boundingBox.height}%`,
              }}
            >
              <div className="absolute -top-6 left-0 bg-rose-600 text-white text-[11px] font-semibold px-2 py-0.5 rounded-t whitespace-nowrap shadow-sm">
                {label || 'Detected Issue'}{' '}
                {confidence != null && `(${(confidence * 100).toFixed(0)}%)`}
              </div>
            </div>
          )}
          <button
            type="button"
            onClick={() => setShowOverlay(!showOverlay)}
            className="absolute bottom-2 right-2 px-2.5 py-1 bg-black/70 hover:bg-black/85 text-white text-xs rounded-lg flex items-center gap-1.5 backdrop-blur-sm transition-all"
          >
            {showOverlay ? <EyeOff size={13} /> : <Eye size={13} />}
            <span>{showOverlay ? 'Hide AI Box' : 'Show AI Box'}</span>
          </button>
        </div>
      );
    }
  }

  // If box is [x1, y1, x2, y2]
  let boxStyle = null;
  if (box && box.length >= 4) {
    const [x1, y1, x2, y2] = box;

    // Check if coordinates are normalized [0..1] or pixel coordinates
    const isNormalized = x1 <= 1.0 && y1 <= 1.0 && x2 <= 1.0 && y2 <= 1.0;

    let leftPct, topPct, widthPct, heightPct;
    if (isNormalized) {
      leftPct = x1 * 100;
      topPct = y1 * 100;
      widthPct = (x2 - x1) * 100;
      heightPct = (y2 - y1) * 100;
    } else if (imageWidth && imageHeight && imageWidth > 0 && imageHeight > 0) {
      leftPct = (x1 / imageWidth) * 100;
      topPct = (y1 / imageHeight) * 100;
      widthPct = ((x2 - x1) / imageWidth) * 100;
      heightPct = ((y2 - y1) / imageHeight) * 100;
    } else {
      // Fallback estimate if image dimensions are not provided
      leftPct = Math.min(Math.max((x1 / 640) * 100, 0), 90);
      topPct = Math.min(Math.max((y1 / 640) * 100, 0), 90);
      widthPct = Math.min(Math.max(((x2 - x1) / 640) * 100, 10), 100 - leftPct);
      heightPct = Math.min(Math.max(((y2 - y1) / 640) * 100, 10), 100 - topPct);
    }

    boxStyle = {
      left: `${Math.max(0, leftPct)}%`,
      top: `${Math.max(0, topPct)}%`,
      width: `${Math.min(100, widthPct)}%`,
      height: `${Math.min(100, heightPct)}%`,
    };
  }

  return (
    <div className={`relative overflow-hidden rounded-xl bg-slate-900 group ${className}`}>
      <img
        src={resolvedSrc}
        alt="Complaint evidence"
        className="w-full h-full object-cover transition-transform duration-300"
      />

      {/* AI Detection overlay badge */}
      {label && (
        <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 bg-slate-900/80 backdrop-blur-md rounded-lg text-white text-xs font-medium border border-white/10 shadow-lg">
          <Sparkles size={13} className="text-amber-400" />
          <span>{label.replace(/_/g, ' ')}</span>
          {confidence != null && (
            <span className="text-emerald-400 font-mono text-[11px]">
              {(confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
      )}

      {/* Bounding Box */}
      {boxStyle && showOverlay && (
        <div
          className="absolute border-2 border-rose-500 bg-rose-500/20 shadow-[0_0_14px_rgba(244,63,94,0.6)] pointer-events-none transition-all duration-200"
          style={boxStyle}
        >
          <div className="absolute -top-6 left-[-2px] bg-rose-600 text-white text-[11px] font-semibold px-2 py-0.5 rounded-t whitespace-nowrap shadow-md">
            {label ? label.replace(/_/g, ' ') : 'Detected Object'}
            {confidence != null && ` • ${(confidence * 100).toFixed(0)}%`}
          </div>
        </div>
      )}

      {/* Toggle button */}
      {boxStyle && (
        <button
          type="button"
          onClick={() => setShowOverlay(!showOverlay)}
          className="absolute bottom-3 right-3 px-2.5 py-1 bg-slate-900/80 hover:bg-slate-900 text-white text-xs rounded-lg flex items-center gap-1.5 backdrop-blur-md border border-white/10 transition-all shadow-md"
        >
          {showOverlay ? <EyeOff size={13} /> : <Eye size={13} />}
          <span>{showOverlay ? 'Hide Box' : 'Show Box'}</span>
        </button>
      )}
    </div>
  );
};

export default DetectionOverlay;
