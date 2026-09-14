import { useState } from 'react';
import { Card, CardContent } from '../../components/ui/card';
import { Skeleton } from '../../components/ui/skeleton';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Cloud, Droplets, Wind, Thermometer, AlertTriangle, ShieldAlert, CloudLightning, Info } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { useMines } from '../../hooks/useMines';

export default function EnvironmentalIntelligence() {
  const { data: mines, isLoading: isLoadingMines } = useMines();
  const [selectedMineId, setSelectedMineId] = useState<string | null>(null);

  const { data: weather, isLoading: isLoadingWeather, isError, refetch } = useQuery({
    queryKey: ['weather-risk', selectedMineId],
    queryFn: async () => {
      if (!selectedMineId) return null;
      const { data } = await apiClient.get(`/api/v1/weather/risk/${selectedMineId}`);
      return data;
    },
    enabled: !!selectedMineId,
  });

  const acknowledgeMutation = useMutation({
    mutationFn: async (id: string) => apiClient.post('/api/v1/weather/risk/' + id + '/acknowledge'),
    onSuccess: () => { alert('Environmental risk acknowledged and recorded in Audit Trail.'); refetch(); }
  });

  const selectedMine = mines?.find((m: any) => m.id === selectedMineId);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Environmental Intelligence</h1>
          <p className="text-gray-500">Real-time weather monitoring and advisory risk assessment.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-1 border-r pr-4">
          <h2 className="text-sm font-semibold text-gray-500 uppercase mb-4">Select Mine</h2>
          {isLoadingMines ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <div className="space-y-2 h-[600px] overflow-y-auto">
              {mines?.map(m => (
                <button
                  key={m.id}
                  onClick={() => setSelectedMineId(m.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedMineId === m.id ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-medium text-sm text-gray-900">{m.name}</div>
                  <div className="text-xs text-gray-500 truncate">{m.location || 'Location unknown'}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="md:col-span-3">
          {!selectedMineId ? (
            <Card className="h-full flex items-center justify-center bg-gray-50 border-dashed min-h-[400px]">
              <div className="text-center text-gray-500">
                <Cloud className="h-12 w-12 mx-auto text-gray-300 mb-2" />
                <p>Select a mine to view environmental intelligence.</p>
              </div>
            </Card>
          ) : isLoadingWeather ? (
            <div className="space-y-4">
              <Skeleton className="h-40 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          ) : isError || weather?.status === 'error' ? (
            <Card className="h-full flex items-center justify-center bg-red-50 border-red-100 min-h-[400px]">
              <div className="text-center text-red-500 max-w-sm">
                <AlertTriangle className="h-12 w-12 mx-auto text-red-300 mb-2" />
                <p className="font-medium mb-4">{weather?.message || 'Weather provider is temporarily unavailable or location is missing.'}</p>
                <Button variant="outline" onClick={() => refetch()}>Retry Request</Button>
              </div>
            </Card>
          ) : weather ? (
            <div className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{selectedMine?.name}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-sm text-gray-500">{selectedMine?.location}</span>
                    <Badge variant="outline" className="bg-gray-100">{weather.weather.provider} Data</Badge>
                    {weather.cached && <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Cached</Badge>}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${
                    weather.advisory_risk_level === 'SEVERE' ? 'text-red-600' :
                    weather.advisory_risk_level === 'ELEVATED' ? 'text-orange-600' : 'text-green-600'
                  }`}>
                    {weather.advisory_risk_level}
                  </div>
                  <div className="text-xs font-semibold text-gray-500 uppercase mt-1">Environmental Risk</div>
                </div>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4 flex items-center gap-4">
                    <Thermometer className="w-8 h-8 text-orange-500" />
                    <div>
                      <div className="text-2xl font-bold">{weather.weather.temperature}°C</div>
                      <div className="text-xs text-gray-500 uppercase">Temperature</div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-4">
                    <Droplets className="w-8 h-8 text-blue-500" />
                    <div>
                      <div className="text-2xl font-bold">{weather.weather.rainfall_mm} mm</div>
                      <div className="text-xs text-gray-500 uppercase">Rainfall</div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-4">
                    <Wind className="w-8 h-8 text-teal-500" />
                    <div>
                      <div className="text-2xl font-bold">{weather.weather.wind_speed} km/h</div>
                      <div className="text-xs text-gray-500 uppercase">Wind</div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 flex items-center gap-4">
                    <CloudLightning className="w-8 h-8 text-purple-500" />
                    <div>
                      <div className="text-lg font-bold truncate max-w-[80px]" title={weather.weather.condition.replace(/_/g, ' ')}>
                        {weather.weather.condition.replace(/_/g, ' ').toUpperCase()}
                      </div>
                      <div className="text-xs text-gray-500 uppercase">Condition</div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="border-l-4 border-l-blue-500">
                <CardContent className="p-6">
                  <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-blue-500" />
                    AI/Environmental Recommendation
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700">Identified Factors:</h4>
                      <ul className="list-disc pl-5 mt-1 text-sm text-gray-600">
                        {weather.assessment.factors.map((f: string, i: number) => <li key={i}>{f}</li>)}
                        {weather.open_water_hazards > 0 && (
                          <li className="text-orange-600 font-medium">{weather.open_water_hazards} unresolved water/drainage hazards currently exist at this mine.</li>
                        )}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700">Recommended Action:</h4>
                      <ul className="list-disc pl-5 mt-1 text-sm text-gray-600">
                        {weather.assessment.recommendations.map((r: string, i: number) => <li key={i}>{r}</li>)}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <Info className="w-4 h-4" />
                      {weather.disclaimer}
                    </div>
                    {weather.advisory_risk_level !== 'LOW' && (
                      <Button size="sm" onClick={() => acknowledgeMutation.mutate(selectedMineId)} disabled={acknowledgeMutation.isPending}>
                        Acknowledge & Action
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>

              <div className="text-xs text-right text-gray-400">
                Observation Time: {new Date(weather.weather.timestamp).toLocaleString()}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}



