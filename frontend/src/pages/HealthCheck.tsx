import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { HealthResponse } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Activity, RefreshCcw, Server, Database, Cloud, FileText, FileSearch, ShieldCheck } from 'lucide-react';
import { formatDateTime } from '../utils/format';

export function HealthCheck() {
  // Using a mock health response if backend is not available yet for UI demonstration
  const [useMock, setUseMock] = useState(false);
  const { data, loading, error, refetch } = useApi<HealthResponse>('/health', { immediate: !useMock });

  const mockData: HealthResponse = {
    status: 'healthy',
    database: 'connected',
    redis: 'connected',
    version: '0.1.0',
    providers: {
      ai: 'operational',
      weather: 'operational',
      ocr: 'degraded',
      storage: 'operational'
    }
  };

  const healthData = useMock ? mockData : data;
  const isHealthy = healthData?.status === 'healthy';

  const handleRefresh = async () => {
    if (!useMock) {
      await refetch();
    }
  };

  const renderStatusCard = (title: string, status: string, provider: string, icon: React.ReactNode) => {
    let variant: 'healthy' | 'warning' | 'elevated' | 'critical' | 'info' | 'inactive' = 'inactive';
    if (status === 'connected' || status === 'operational') variant = 'healthy';
    else if (status === 'degraded') variant = 'warning';
    else if (status === 'disconnected' || status === 'error') variant = 'critical';

    return (
      <div className="bg-white rounded-card border border-graphite-100 shadow-card p-5 flex flex-col gap-3 transition-shadow hover:shadow-elevated">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-md bg-graphite-50 text-graphite-600">
              {icon}
            </div>
            <div>
              <h3 className="font-medium text-graphite-900">{title}</h3>
              <p className="text-xs text-graphite-500 mt-0.5">{provider}</p>
            </div>
          </div>
          <StatusBadge variant={variant} dot size="sm">
            {status}
          </StatusBadge>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-graphite-900 tracking-tight flex items-center gap-2">
            <Activity className="text-mining-amber-500" />
            System Health Status
          </h1>
          <p className="text-graphite-500 mt-1">CoalMine Governance Platform diagnostics and service availability</p>
        </div>
        
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-graphite-600">
            <input 
              type="checkbox" 
              checked={useMock} 
              onChange={(e) => setUseMock(e.target.checked)}
              className="rounded border-graphite-300 text-mining-amber-500 focus:ring-mining-amber-500"
            />
            Use Mock Data
          </label>
          <button 
            onClick={handleRefresh}
            disabled={loading && !useMock}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-graphite-200 text-graphite-700 rounded-md hover:bg-graphite-50 hover:text-graphite-900 transition-colors text-sm font-medium disabled:opacity-50"
          >
            <RefreshCcw size={16} className={(loading && !useMock) ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {error && !useMock ? (
        <div className="bg-white rounded-card border border-graphite-100 shadow-card p-6 bg-red-50 border-red-200 flex flex-col items-center text-center justify-center py-12">
          <Activity size={48} className="text-red-300 mb-4" />
          <h2 className="text-lg font-semibold text-red-800">Connection Failed</h2>
          <p className="text-red-600 mt-1 mb-6 max-w-md">Could not reach the health endpoint. Ensure the backend server is running.</p>
          <p className="text-xs font-mono text-red-500 bg-white p-2 rounded border border-red-100">{error}</p>
        </div>
      ) : loading && !useMock ? (
        <div className="bg-white rounded-card border border-graphite-100 shadow-card p-12 flex flex-col items-center justify-center min-h-[400px]">
          <div className="w-10 h-10 border-4 border-graphite-100 border-t-mining-amber-500 rounded-full animate-spin mb-4"></div>
          <p className="text-graphite-500 font-medium">Checking system health...</p>
        </div>
      ) : healthData ? (
        <div className="space-y-6">
          <div className="bg-white rounded-card border border-graphite-100 shadow-card p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-gradient-to-r from-graphite-950 to-graphite-900 text-white overflow-hidden relative">
            {/* Abstract background shape */}
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-mining-amber-500/10 rounded-full blur-3xl"></div>
            
            <div className="relative z-10">
              <h2 className="text-lg font-semibold text-white/90">Overall Status</h2>
              <div className="flex items-center gap-3 mt-2">
                <StatusBadge 
                  variant={isHealthy ? 'healthy' : 'warning'} 
                  dot 
                  className={isHealthy ? "bg-green-500/20 text-green-300 border-green-500/30" : "bg-amber-500/20 text-amber-300 border-amber-500/30"}
                >
                  {isHealthy ? 'All systems operational' : 'System degraded'}
                </StatusBadge>
                <span className="text-sm text-graphite-400 font-mono">v{healthData.version}</span>
              </div>
            </div>
            
            <div className="relative z-10 text-right sm:text-left">
              <p className="text-xs text-graphite-400 uppercase tracking-wider font-semibold">Last Checked</p>
              <p className="text-sm text-graphite-200 mt-1">{formatDateTime(new Date())}</p>
            </div>
          </div>

          <div>
            <h3 className="section-header mb-4">Core Infrastructure</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {renderStatusCard('Database', healthData.database, 'PostgreSQL 16', <Database size={20} />)}
              {renderStatusCard('Cache & Queue', healthData.redis, 'Redis', <Server size={20} />)}
              {renderStatusCard('API Gateway', 'connected', 'FastAPI', <Cloud size={20} />)}
            </div>
          </div>

          <div>
            <h3 className="section-header mb-4">External Services</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {renderStatusCard('AI Engine', healthData.providers.ai, 'Provider: ' + healthData.providers.ai, <Activity size={20} />)}
              {renderStatusCard('OCR Service', healthData.providers.ocr, 'Provider: ' + healthData.providers.ocr, <FileSearch size={20} />)}
              {renderStatusCard('Weather API', healthData.providers.weather, 'Provider: ' + healthData.providers.weather, <Cloud size={20} />)}
              {renderStatusCard('Document Storage', healthData.providers.storage, 'Provider: ' + healthData.providers.storage, <FileText size={20} />)}
              {renderStatusCard('Compliance Engine', 'operational', 'Internal Rule Engine', <ShieldCheck size={20} />)}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
