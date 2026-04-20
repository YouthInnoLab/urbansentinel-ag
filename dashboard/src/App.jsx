import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { ShieldAlert, Activity, Shield, MapPin, RadioTower, AlertTriangle } from 'lucide-react';
import './index.css';

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [systemStatus, setSystemStatus] = useState('Connecting');

  useEffect(() => {
    const connectWs = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

      ws.onopen = () => {
        setSystemStatus('Active. Securing City.');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setAlerts((prev) => [data, ...prev]);
        } catch (e) {
          console.error(e);
        }
      };

      ws.onclose = () => {
        setSystemStatus('Disconnected. Retrying...');
        setTimeout(connectWs, 3000);
      };
      
      return ws;
    };
    
    let ws = connectWs();
    return () => {
      if(ws) ws.close();
    };
  }, []);

  // NYC center roughly
  const center = [40.7128, -74.0060];

  return (
    <div className="h-screen w-full relative overflow-hidden bg-[#0b0c10] text-[#c5c6c7] font-sans">
      
      {/* Dynamic Map Layer */}
      <div className="absolute inset-0 z-0">
        <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%', background: '#0b0c10' }}>
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
          {alerts.map((alert, idx) => (
            <CircleMarker 
              key={idx} 
              center={[alert.lat, alert.lon]} 
              radius={10 + (alert.confidence * 10)}
              pathOptions={{ 
                color: alert.alert_type === 'Gunshot' ? '#ff3b30' : '#ff9500',
                fillColor: alert.alert_type === 'Gunshot' ? '#ff3b30' : '#ff9500',
                fillOpacity: 0.6
              }}
              className="pulse-marker"
            >
              <Popup className="custom-popup">
                <div className="font-bold text-lg text-white mb-1">{alert.alert_type} Detected</div>
                <div className="text-sm opacity-80">Node ID: {alert.node_id}</div>
                <div className="text-sm opacity-80">Confidence: {(alert.confidence * 100).toFixed(1)}%</div>
                <div className="text-xs opacity-50 mt-2">{new Date(alert.timestamp).toLocaleTimeString()}</div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Floating UI Elements (Glassmorphism) */}
      <div className="absolute inset-y-0 left-0 z-10 w-96 p-6 pointer-events-none flex flex-col">
        {/* Header Panel */}
        <div className="glass-panel p-6 rounded-2xl mb-6 pointer-events-auto border border-white/10 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
          <div className="flex items-center gap-4 mb-2">
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(0,255,255,0.4)]">
              <Shield className="text-white w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-white tracking-tight">UrbanSentinel</h1>
              <p className="text-xs uppercase tracking-widest text-[#66fcf1]">Edge AI Security</p>
            </div>
          </div>
          
          <div className="my-4 h-[1px] w-full bg-gradient-to-r from-white/10 via-white/20 to-transparent"></div>
          
          <div className="flex items-center gap-3 mt-4">
            <span className="relative flex h-3 w-3">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${systemStatus.includes('Active') ? 'bg-[#66fcf1]' : 'bg-red-500'}`}></span>
              <span className={`relative inline-flex rounded-full h-3 w-3 ${systemStatus.includes('Active') ? 'bg-[#66fcf1]' : 'bg-red-500'}`}></span>
            </span>
            <span className="text-sm font-medium tracking-wide text-white/80">System: {systemStatus}</span>
          </div>
        </div>

        {/* Realtime Alert Feed */}
        <div className="glass-panel p-5 rounded-2xl flex-grow pointer-events-auto border border-white/10 shadow-2xl flex flex-col overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#66fcf1]" />
              Live Alerts
            </h2>
            <span className="bg-red-500/20 text-red-400 text-xs py-1 px-2 rounded-full border border-red-500/30">
              {alerts.length} Incidents
            </span>
          </div>
          
          <div className="flex-grow overflow-y-auto pr-2 custom-scrollbar space-y-3">
            {alerts.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-white/40 space-y-4">
                <RadioTower className="w-12 h-12 stroke-[1.5]" />
                <p className="text-sm">Monitoring city acoustic data locally. No PII transmitted.</p>
              </div>
            ) : (
              alerts.map((alert, idx) => (
                <div key={idx} className="bg-white/5 hover:bg-white/10 border-l-4 border-red-500 p-4 rounded-r-lg transition-all cursor-pointer group animate-slideIn">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 text-white font-semibold">
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                        {alert.alert_type}
                      </div>
                      <div className="text-xs text-white/50 mt-1 flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> Node {alert.node_id}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs font-mono text-[#66fcf1]">
                        {new Date(alert.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}
                      </div>
                      <div className="text-xs text-white/40 mt-1">Conf: {(alert.confidence*100).toFixed(0)}%</div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
