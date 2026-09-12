import { useParams } from 'react-router-dom';
import { useMine } from '../../hooks/useMines';
import { useOperations } from '../../hooks/useOperations';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Activity, Wind, Droplets, Users, Target, CheckCircle2 } from 'lucide-react';

export default function MineDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: mine, isLoading: isMineLoading } = useMine(id || '');
  const { environment, production, contractors, isEnvLoading, isProdLoading, isContractorsLoading } = useOperations(id || '');

  if (isMineLoading) return <div className="p-6">Loading mine details...</div>;
  if (!mine) return <div className="p-6">Mine not found</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{mine.name}</h1>
        <p className="text-gray-500">{mine.location} • {mine.status}</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="production">Production</TabsTrigger>
          <TabsTrigger value="environment">Environment</TabsTrigger>
          <TabsTrigger value="contractors">Contractors</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>Mine Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500">Location</h3>
                <p className="mt-1 text-sm text-gray-900">{mine.location}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Status</h3>
                <p className="mt-1 text-sm text-gray-900">{mine.status}</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="production">
          <Card>
            <CardHeader>
              <CardTitle>Production Data</CardTitle>
              <CardDescription>Target vs Actual production figures</CardDescription>
            </CardHeader>
            <CardContent>
              {isProdLoading ? (
                <p>Loading production data...</p>
              ) : production?.length ? (
                <div className="space-y-4">
                  {production.map((p: any, idx: any) => (
                    <div key={idx} className="flex items-center justify-between p-4 border rounded-lg bg-gray-50">
                      <div>
                        <p className="font-medium">{new Date(p.date).toLocaleDateString()}</p>
                      </div>
                      <div className="flex space-x-6">
                        <div className="flex items-center space-x-2">
                          <Target className="w-4 h-4 text-gray-500" />
                          <div>
                            <p className="text-sm text-gray-500">Target</p>
                            <p className="font-semibold">{p.target_tons} tons</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                          <div>
                            <p className="text-sm text-gray-500">Actual</p>
                            <p className="font-semibold">{p.actual_tons} tons</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No production data available.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="environment">
          <Card>
            <CardHeader>
              <CardTitle>Environmental Readings</CardTitle>
              <CardDescription>Air, Dust, and Water quality readings</CardDescription>
            </CardHeader>
            <CardContent>
              {isEnvLoading ? (
                <p>Loading environment data...</p>
              ) : environment?.length ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {environment.map((env: any, idx: any) => (
                    <div key={idx} className="col-span-full grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 pb-4 border-b last:border-0 last:mb-0 last:pb-0">
                      <div className="p-4 border rounded-lg bg-primary-50 flex items-start space-x-3">
                        <Wind className="w-5 h-5 text-primary-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-primary-600 font-medium">Air Quality Index</p>
                          <p className="text-2xl font-bold text-primary-900">{env.air_quality_index}</p>
                          <p className="text-xs text-primary-400 mt-1">{new Date(env.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="p-4 border rounded-lg bg-orange-50 flex items-start space-x-3">
                        <Activity className="w-5 h-5 text-orange-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-orange-600 font-medium">Dust PM10</p>
                          <p className="text-2xl font-bold text-orange-900">{env.dust_pm10}</p>
                          <p className="text-xs text-orange-400 mt-1">{new Date(env.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="p-4 border rounded-lg bg-cyan-50 flex items-start space-x-3">
                        <Droplets className="w-5 h-5 text-cyan-500 mt-0.5" />
                        <div>
                          <p className="text-sm text-cyan-600 font-medium">Water pH</p>
                          <p className="text-2xl font-bold text-cyan-900">{env.water_ph}</p>
                          <p className="text-xs text-cyan-400 mt-1">{new Date(env.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No environmental data available.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contractors">
          <Card>
            <CardHeader>
              <CardTitle>Contractors Overview</CardTitle>
              <CardDescription>Active contractors and worker counts</CardDescription>
            </CardHeader>
            <CardContent>
              {isContractorsLoading ? (
                <p>Loading contractors...</p>
              ) : contractors?.length ? (
                <div className="space-y-4">
                  {contractors.map((c: any) => (
                    <div key={c.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                          <Users className="w-5 h-5 text-gray-500" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">{c.name}</p>
                          <p className="text-sm text-gray-500">Status: {c.status}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold">{c.workers_count}</p>
                        <p className="text-sm text-gray-500">Workers</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No contractors registered.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
