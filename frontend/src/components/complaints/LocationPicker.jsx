import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapPin, Navigation } from 'lucide-react';

// Fix Leaflet marker icon asset resolution
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Component to handle map clicks
const LocationMarker = ({ position, setPosition, onLocationSelect }) => {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      const coords = { lat: Number(lat.toFixed(6)), lng: Number(lng.toFixed(6)) };
      setPosition(coords);
      onLocationSelect(coords);
    },
  });

  return position === null ? null : <Marker position={[position.lat, position.lng]} />;
};

// Smoothly re-center map when location is chosen programmatically
const MapRecenter = ({ position }) => {
  const map = useMap();
  useEffect(() => {
    if (position) {
      map.flyTo([position.lat, position.lng], 15, { duration: 1.2 });
    }
  }, [position, map]);
  return null;
};

const LocationPicker = ({ onLocationSelect, initialPosition = null }) => {
  const [position, setPosition] = useState(initialPosition);
  const [locating, setLocating] = useState(false);
  // Default center
  const defaultCenter = [12.9716, 77.5946]; // Bangalore civic center default
  const zoom = 12;

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }

    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (loc) => {
        setLocating(false);
        const newPos = {
          lat: Number(loc.coords.latitude.toFixed(6)),
          lng: Number(loc.coords.longitude.toFixed(6)),
        };
        setPosition(newPos);
        onLocationSelect(newPos);
      },
      (error) => {
        setLocating(false);
        console.error('Error obtaining geolocation:', error);
        alert('Could not retrieve your location. Please click anywhere on the map to pin.');
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  return (
    <div className="w-full flex flex-col gap-2">
      <div className="flex justify-between items-center text-xs">
        <span className="text-slate-600 font-medium flex items-center gap-1">
          <MapPin size={14} className="text-blue-600" />
          {position ? (
            <span className="font-mono text-slate-800">
              {position.lat}, {position.lng}
            </span>
          ) : (
            <span className="text-slate-400">Click on the map or use GPS to set coordinates</span>
          )}
        </span>
        <button
          type="button"
          onClick={handleGetCurrentLocation}
          disabled={locating}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors disabled:opacity-50"
        >
          <Navigation size={12} className={locating ? 'animate-spin' : ''} />
          {locating ? 'Locating...' : 'Use My GPS'}
        </button>
      </div>

      <div className="h-64 w-full rounded-xl overflow-hidden border border-slate-300 relative shadow-inner z-0">
        <MapContainer
          center={position ? [position.lat, position.lng] : defaultCenter}
          zoom={position ? 15 : zoom}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <LocationMarker
            position={position}
            setPosition={setPosition}
            onLocationSelect={onLocationSelect}
          />
          <MapRecenter position={position} />
        </MapContainer>
      </div>
    </div>
  );
};

export default LocationPicker;
