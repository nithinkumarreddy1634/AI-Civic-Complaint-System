import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Link } from 'react-router-dom';
import adminService from '../services/adminService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ExternalLink, Map, RefreshCw } from 'lucide-react';

const PRIORITY_COLORS = {
  URGENT: '#f43f5e',
  HIGH: '#8b5cf6',
  MEDIUM: '#3b82f6',
  LOW: '#64748b',
};

// Ensure map container renders tiles correctly and pans smoothly
const MapController = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    // Invalidate size on mount to avoid grey/invisible tile issues in flex containers
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 150);
    if (center && center[0] != null && center[1] != null) {
      map.setView(center, map.getZoom());
    }
    return () => clearTimeout(timer);
  }, [map, center]);
  return null;
};

const AdminMapPage = () => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const fetchAll = async () => {
    setLoading(true);
    try {
      // Fetch up to 100 geo-tagged complaints
      const data = await adminService.getAllComplaints({ limit: 100 });
      const items = data.items || data || [];
      const validGeo = (Array.isArray(items) ? items : []).filter(
        (c) => c.latitude != null && c.longitude != null && !isNaN(c.latitude) && !isNaN(c.longitude)
      );
      setComplaints(validGeo);
    } catch (err) {
      console.error('Failed to load complaints for map:', err);
      setComplaints([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const filtered = priorityFilter === 'ALL'
    ? complaints
    : complaints.filter((c) => {
        const p = c.priority_level || c.priority?.priority_level || c.priority?.level || (typeof c.priority === 'string' ? c.priority : 'LOW');
        return p === priorityFilter;
      });

  const center = filtered.length > 0
    ? [filtered[0].latitude, filtered[0].longitude]
    : [12.9716, 77.5946];

  if (loading) return <LoadingSpinner fullScreen />;

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-[#111827] border border-slate-800 p-5 rounded-2xl shadow-xl">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Map size={22} className="text-purple-400" />
            Live Incident Map
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Displaying {filtered.length} geo-tagged incident{filtered.length !== 1 ? 's' : ''} across monitored zones
          </p>
        </div>

        {/* Priority filter and Refresh */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 bg-[#161F30] p-1 rounded-xl border border-slate-700/60">
            {['ALL', 'URGENT', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  priorityFilter === p
                    ? 'bg-purple-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          <button
            onClick={fetchAll}
            className="p-2 rounded-xl bg-[#161F30] border border-slate-700/60 text-slate-400 hover:text-white transition-colors"
            title="Refresh Map Incidents"
          >
            <RefreshCw size={15} />
          </button>
        </div>
      </div>

      {/* Legend & Stats Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3 bg-[#111827]/80 border border-slate-800 rounded-xl text-xs text-slate-400 shadow-sm">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="font-semibold text-slate-300">Priority Levels:</span>
          {Object.entries(PRIORITY_COLORS).map(([level, color]) => (
            <div key={level} className="flex items-center gap-1.5 font-medium">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
              <span>{level}</span>
            </div>
          ))}
        </div>
        <div className="text-[11px] font-mono text-purple-400">
          OpenStreetMap &bull; Leaflet Engine
        </div>
      </div>

      {/* Map Viewport Container with Guaranteed Explicit Dimensions */}
      <div
        className="w-full rounded-2xl overflow-hidden border border-slate-800 shadow-2xl relative z-0"
        style={{ height: 'calc(100vh - 270px)', minHeight: '520px' }}
      >
        <MapContainer
          center={center}
          zoom={filtered.length > 1 ? 11 : 13}
          style={{ height: '100%', width: '100%', zIndex: 1 }}
          scrollWheelZoom={true}
        >
          <MapController center={center} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filtered.map((c) => {
            const priority = c.priority_level || c.priority?.priority_level || c.priority?.level || (typeof c.priority === 'string' ? c.priority : 'LOW');
            const color = PRIORITY_COLORS[priority] || PRIORITY_COLORS.LOW;
            return (
              <CircleMarker
                key={c.id}
                center={[c.latitude, c.longitude]}
                radius={priority === 'URGENT' ? 14 : priority === 'HIGH' ? 11 : 9}
                pathOptions={{
                  color: '#ffffff',
                  fillColor: color,
                  fillOpacity: 0.85,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="text-xs min-w-[200px] p-1 font-sans text-slate-800">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-slate-900 capitalize text-sm">
                        {c.category?.replace(/_/g, ' ') || 'Civic Incident'}
                      </span>
                      <span
                        className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white uppercase"
                        style={{ backgroundColor: color }}
                      >
                        {priority}
                      </span>
                    </div>
                    <p className="text-slate-600 mb-2.5 line-clamp-2 leading-relaxed">
                      {c.description || 'No description provided'}
                    </p>
                    {c.address && (
                      <p className="text-[11px] text-slate-500 mb-2 flex items-center gap-1">
                        📍 {c.address}
                      </p>
                    )}
                    <div className="pt-2 border-t border-slate-200 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-slate-400">
                        #{String(c.id).substring(0, 8)}
                      </span>
                      <Link
                        to={`/admin/complaints/${c.id}`}
                        className="text-purple-600 hover:text-purple-800 font-semibold flex items-center gap-1 text-[11px]"
                      >
                        View Details <ExternalLink size={11} />
                      </Link>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
};

export default AdminMapPage;
