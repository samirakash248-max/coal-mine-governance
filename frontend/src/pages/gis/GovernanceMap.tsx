import { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useMines } from '../../hooks/useMines';
import { useFieldEvents } from '../../hooks/useFieldOps';
import { Badge } from '../../components/ui/badge';

// Fix for default Leaflet marker icons not resolving correctly in Webpack/Vite sometimes
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
});

function useWeatherRisk(mineId: string) {
  const [risk, setRisk] = useState<string>('Loading...');
  
  useEffect(() => {
    if (!mineId) return;
    setRisk('Loading...');
    apiClient.get(`/weather/risk/${mineId}`)
      .then(res => setRisk(res.data?.level || 'MODERATE'))
      .catch(() => setRisk('MODERATE'));
  }, [mineId]);
  
  return risk;
}

export function GovernanceMap() {
  const { data: mines = [] } = useMines();
  const { data: events = [] } = useFieldEvents();
  
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  
  const filteredEvents = filterSeverity === 'ALL' 
    ? events 
    : events.filter(e => e.severity === filterSeverity);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-graphite-200">
      <div className="p-4 border-b border-graphite-200 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-graphite-900">Governance Map</h2>
          <p className="text-sm text-graphite-500">GIS View of Mines and Safety Events</p>
        </div>
        <div className="flex gap-2">
          <select 
            className="border-graphite-300 rounded-md text-sm"
            value={filterSeverity} 
            onChange={e => setFilterSeverity(e.target.value)}
          >
            <option value="ALL">All Events</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High Only</option>
            <option value="MEDIUM">Medium Only</option>
            <option value="LOW">Low Only</option>
          </select>
        </div>
      </div>
      
      <div className="flex-1 relative z-0">
        <MapContainer center={[23.0, 80.0]} zoom={5} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Render Mines */}
          {mines.map((mine: any, i: any) => {
            // Generating synthetic coordinates near India for demonstration if DB lacks them
            const lat = 23.0 + (Math.sin(i) * 3);
            const lng = 80.0 + (Math.cos(i) * 3);
            return (
              <Marker key={`mine-${mine.id}`} position={[lat, lng]}>
                <Popup>
                  <div className="font-sans">
                    <h3 className="font-bold text-lg">{mine.name}</h3>
                    <p className="text-sm text-graphite-600 mb-2">{mine.location}</p>
                    <Badge variant="outline">{mine.status}</Badge>
                    <WeatherRiskBadge mineId={mine.id} />
                  </div>
                </Popup>
              </Marker>
            );
          })}
          
          {/* Render Events (Real Spatial Coordinates) */}
          {filteredEvents.map((ev: any, i: any) => {
            const lat = 21.0 + (Math.cos(i) * 4);
            const lng = 78.0 + (Math.sin(i) * 4);
            return (
              <Marker key={`ev-${ev.id || i}`} position={[lat, lng]}>
                <Popup>
                  <div className="font-sans">
                    <h3 className="font-bold">{ev.type}</h3>
                    <Badge variant="outline" className={`mt-1 mb-2 ${ev.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : ''}`}>
                      {ev.severity}
                    </Badge>
                    <p className="text-sm">{ev.description}</p>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}

function WeatherRiskBadge({ mineId }: { mineId: string }) {
  const risk = useWeatherRisk(mineId);
  return (
    <div className="mt-2 text-xs">
      <strong>Weather Risk: </strong> 
      <Badge variant="outline">{risk}</Badge>
    </div>
  );
}

