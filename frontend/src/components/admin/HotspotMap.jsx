import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const HotspotMap = ({ hotspots = [] }) => {
  const center = [20.5937, 78.9629]; // Default India
  
  // Find color based on density/count
  const getColor = (count) => {
    if (count > 20) return '#ef4444'; // Red
    if (count > 10) return '#f97316'; // Orange
    if (count > 5) return '#eab308'; // Yellow
    return '#3b82f6'; // Blue
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 h-[500px] flex flex-col">
      <h3 className="font-semibold text-gray-800 mb-4">Complaint Hotspots</h3>
      <div className="flex-1 rounded-lg overflow-hidden relative z-0">
        <MapContainer center={center} zoom={5} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {hotspots.map((spot, idx) => (
            <CircleMarker
              key={idx}
              center={[spot.lat, spot.lng]}
              radius={Math.min(Math.max(spot.count * 2, 8), 30)}
              pathOptions={{
                color: getColor(spot.count),
                fillColor: getColor(spot.count),
                fillOpacity: 0.6,
                weight: 2
              }}
            >
              <Popup>
                <div className="text-sm">
                  <p className="font-semibold mb-1">Hotspot Activity</p>
                  <p>Total Complaints: {spot.count}</p>
                  <p>Primary Issue: {spot.primaryCategory}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      <div className="mt-4 flex items-center justify-center gap-6 text-xs text-gray-600">
        <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-blue-500 opacity-60"></span> Low (1-5)</div>
        <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-yellow-500 opacity-60"></span> Medium (6-10)</div>
        <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-500 opacity-60"></span> High (11-20)</div>
        <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500 opacity-60"></span> Severe (20+)</div>
      </div>
    </div>
  );
};

export default HotspotMap;
