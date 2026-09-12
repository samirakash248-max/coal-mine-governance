import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { AlertCircle, FileText, Activity, Users, Inbox } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useFieldEventStats, useFieldEvents } from '../hooks/useFieldOps';

export default function Safety() {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading } = useFieldEventStats();
  const { data: events, isLoading: eventsLoading } = useFieldEvents();

  const loading = statsLoading || eventsLoading;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Safety Dashboard</h1>
        <button
          onClick={() => navigate('/safety/report-near-miss')}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Report Near Miss
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {loading ? (
          [...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6 flex items-center space-x-4">
                <Skeleton className="w-10 h-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-6 w-12" />
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <AlertCircle className="w-10 h-10 text-red-500" />
                <div>
                  <p className="text-sm text-gray-500">Total Events</p>
                  <h3 className="text-2xl font-bold">{stats?.total_events || 0}</h3>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <FileText className="w-10 h-10 text-yellow-500" />
                <div>
                  <p className="text-sm text-gray-500">Near Misses</p>
                  <h3 className="text-2xl font-bold">{stats?.near_misses || 0}</h3>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <Activity className="w-10 h-10 text-orange-500" />
                <div>
                  <p className="text-sm text-gray-500">Incidents</p>
                  <h3 className="text-2xl font-bold">{stats?.incidents || 0}</h3>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <Users className="w-10 h-10 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-500">Critical Hazards</p>
                  <h3 className="text-2xl font-bold">{stats?.critical_hazards || 0}</h3>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Safety Events</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="p-4">Date</th>
                    <th className="p-4">Mine ID</th>
                    <th className="p-4">Type</th>
                    <th className="p-4">Severity</th>
                    <th className="p-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(events || []).map((ev: any) => (
                    <tr key={ev.id} className="border-b hover:bg-gray-50">
                      <td className="p-4">{new Date(ev.date || ev.created_at).toLocaleDateString()}</td>
                      <td className="p-4">{ev.mine_id}</td>
                      <td className="p-4">{ev.type}</td>
                      <td className="p-4">
                        <Badge variant={ev.severity === 'CRITICAL' || ev.severity === 'HIGH' ? 'destructive' : (ev.severity === 'MEDIUM' ? 'default' : 'secondary')}>
                          {ev.severity}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <button
                          onClick={() => navigate(`/safety/${ev.id}`)}
                          className="text-blue-600 hover:underline"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                  {(!events || events.length === 0) && (
                    <tr>
                      <td colSpan={5} className="p-12 text-center">
                        <div className="flex flex-col items-center">
                          <Inbox className="w-12 h-12 text-gray-400 mb-3" />
                          <h3 className="text-lg font-medium text-gray-900">No safety events found</h3>
                          <p className="text-gray-500 mt-1">There are no reported safety events yet.</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
