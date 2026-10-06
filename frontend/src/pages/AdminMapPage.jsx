import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Link } from 'react-router-dom';
import adminService from '../services/adminService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ExternalLink, Map } from 'lucide-react';

const PRIORITY_COLORS = {
  URGENT: '#f43f5e',
  HIGH: '#8b5cf6',
  MEDIUM: '#3b82f6',
  LOW: '#64748b',
};

const AdminMapPage = () => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        // Fetch all geo-tagged complaints
        const data = await adminService.getAllComplaints({ limit: 200 });
        const items = data.items || data || [];
        setComplaints(items.filter((c) => c.latitude != null && c.longitude != null));
      } catch (err) {
        console.error('Failed to load complaints:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const filtered = priorityFilter === 'ALL'
    ? complaints
    : complaints.filter((c) => (c.priority_level || c.priority?.level) === priorityFilter);

  const center = filtered.length > 0
    ? [filtered[0].latitude, filtered[0].longitude]
    : [12.9716, 77.5946];

  if (loading) return <LoadingSpinner fullScreen />;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Map size={22} className="text-blue-600" />
            Complaint Map
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">
            {filtered.length} geo-tagged complaint{filtered.length !== 1 ? 's' : ''} visible
          </p>
        </div>
        {/* Priority filter */}
        <div className="flex items-center gap-2">
          {['ALL', 'URGENT', 'HIGH', 'MEDIUM', 'LOW'].map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                priorityFilter === p
                  ? 'bg-slate-900 text-white border-slate-900'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-400'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-3">
        {Object.entries(PRIORITY_COLORS).map(([level, color]) => (
          <div key={level} className="flex items-center gap-1.5 text-xs text-slate-500">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            {level}
          </div>
        ))}
      </div>

      {/* Map */}
      <div className="flex-1 min-h-[500px] rounded-xl overflow-hidden border border-slate-300 shadow-sm z-0">
        <MapContainer
          center={center}
          zoom={filtered.length > 1 ? 10 : 13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filtered.map((c) => {
            const priority = c.priority_level || c.priority?.level || 'LOW';
            const color = PRIORITY_COLORS[priority] || PRIORITY_COLORS.LOW;
            return (
              <CircleMarker
                key={c.id}
                center={[c.latitude, c.longitude]}
                radius={priority === 'URGENT' ? 12 : priority === 'HIGH' ? 10 : 8}
                pathOptions={{
                  color: color,
                  fillColor: color,
                  fillOpacity: 0.75,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="text-xs min-w-[160px]">
                    <p className="font-bold text-slate-800 mb-1 capitalize">
                      {c.category?.replace(/_/g, ' ')}
                    </p>
                    <p className="text-slate-600 mb-2 line-clamp-2">{c.description}</p>
                    <div className="flex items-center justify-between">
                      <span
                        className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white"
                        style={{ backgroundColor: color }}
                      >
                        {priority}
                      </span>
                      <Link
                        to={`/admin/complaints/${c.id}`}
                        className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-[11px] font-medium"
                      >
                        View <ExternalLink size={11} />
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
