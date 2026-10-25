import React, { useState } from 'react';
import { Sparkles, AlertTriangle, Zap, Trash2, Droplets, CircleDot, Check } from 'lucide-react';

export const REAL_EXAMPLES = [
  {
    id: 'pothole',
    label: 'Deep Roadway Pothole',
    category: 'pothole',
    description: 'Hazardous deep crater pothole in the central driving lane causing vehicular damage and sudden braking. Sub-base gravel exposed.',
    address: 'MG Road Junction, Central Ward 84, Bengaluru',
    lat: 12.9716,
    lng: 77.5946,
    imagePath: '/examples/pothole.jpg',
    tag: 'High Traffic Hazard',
    icon: AlertTriangle,
    color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  },
  {
    id: 'broken_streetlight',
    label: 'Broken Streetlight Outage',
    category: 'broken_streetlight',
    description: 'Streetlight pole short-circuit and smashed luminaire casing leaving 120 meters of arterial road and sidewalk completely dark.',
    address: '100 Feet Road, Indiranagar, Bengaluru',
    lat: 12.9784,
    lng: 77.6408,
    imagePath: '/examples/broken_streetlight.jpg',
    tag: 'Public Safety Risk',
    icon: Zap,
    color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
  },
  {
    id: 'garbage_accumulation',
    label: 'Overflowing Waste Dump',
    category: 'garbage_accumulation',
    description: 'Municipal dumpster overflowing with mixed commercial refuse onto pedestrian pavement, attracting strays and clogging storm drain.',
    address: '80 Feet Road, Koramangala 4th Block, Bengaluru',
    lat: 12.9352,
    lng: 77.6245,
    imagePath: '/examples/garbage_accumulation.jpg',
    tag: 'Sanitation Emergency',
    icon: Trash2,
    color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  },
  {
    id: 'water_leakage',
    label: 'Potable Water Pipeline Burst',
    category: 'water_leakage',
    description: 'Underground pressurized clean water distribution main ruptured, submerging two roadway lanes and causing significant erosion.',
    address: '14th Main Road, Sector 2, HSR Layout, Bengaluru',
    lat: 12.9121,
    lng: 77.6446,
    imagePath: '/examples/water_leakage.jpg',
    tag: 'Resource Loss',
    icon: Droplets,
    color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  },
  {
    id: 'open_manhole',
    label: 'Missing Sewer Manhole Cover',
    category: 'open_manhole',
    description: 'Uncovered 4-foot deep stormwater drainage manhole next to public bus stop without warning barriers or safety perimeter cones.',
    address: 'Whitefield Main Road, Near ITPL, Bengaluru',
    lat: 12.9698,
    lng: 77.7499,
    imagePath: '/examples/open_manhole.jpg',
    tag: 'Critical Fall Hazard',
    icon: CircleDot,
    color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  },
];

const RealExamplePresets = ({ onSelectPreset, currentCategory }) => {
  const [loadingPreset, setLoadingPreset] = useState(null);
  const [activePresetId, setActivePresetId] = useState(null);

  const handleSelect = async (example) => {
    setLoadingPreset(example.id);
    try {
      // Fetch the real sample image file from public folder
      const res = await fetch(example.imagePath);
      const blob = await res.blob();
      const file = new File([blob], `${example.id}.jpg`, { type: 'image/jpeg' });

      setActivePresetId(example.id);
      onSelectPreset({
        category: example.category,
        description: example.description,
        address: example.address,
        location: { lat: example.lat, lng: example.lng },
        image: file,
      });
    } catch (err) {
      console.error('Failed to load example preset:', err);
    } finally {
      setLoadingPreset(null);
    }
  };

  return (
    <div className="bg-[#111827]/95 border border-purple-500/30 rounded-2xl p-5 mb-6 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-purple-600/20 text-purple-400 flex items-center justify-center">
            <Sparkles size={16} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Real-World Examples & Quick Testing
            </h3>
            <p className="text-xs text-slate-400">
              One-click populate realistic civic infrastructure complaints with verified photos and GPS coordinates
            </p>
          </div>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-300 border border-purple-500/20 w-fit">
          5 Real Presets
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
        {REAL_EXAMPLES.map((ex) => {
          const Icon = ex.icon;
          const isSelected = activePresetId === ex.id;
          const isLoading = loadingPreset === ex.id;

          return (
            <button
              key={ex.id}
              type="button"
              onClick={() => handleSelect(ex)}
              disabled={isLoading}
              className={`text-left p-3 rounded-xl border transition-all duration-200 flex flex-col justify-between group ${
                isSelected
                  ? 'bg-purple-950/60 border-purple-500 shadow-md shadow-purple-500/20 ring-1 ring-purple-500'
                  : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold border ${ex.color}`}>
                    <Icon size={11} />
                    <span>{ex.tag}</span>
                  </span>
                  {isSelected && (
                    <span className="w-4 h-4 rounded-full bg-purple-600 text-white flex items-center justify-center text-[10px]">
                      <Check size={10} />
                    </span>
                  )}
                </div>
                <h4 className="text-xs font-bold text-slate-200 group-hover:text-white transition-colors line-clamp-1">
                  {ex.label}
                </h4>
                <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-snug">
                  {ex.address}
                </p>
              </div>

              <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-semibold text-purple-400 group-hover:text-purple-300">
                <span>{isLoading ? 'Loading...' : isSelected ? 'Applied ✓' : 'Click to Load'}</span>
                <span>&rarr;</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default RealExamplePresets;
