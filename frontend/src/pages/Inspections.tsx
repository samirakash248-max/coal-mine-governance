import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Skeleton } from '../components/ui/skeleton';
import { ClipboardList, AlertTriangle, CheckCircle, Clock, Inbox } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useInspectionStats, useInspectionsList } from '../hooks/useInspections';

export default function Inspections() {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading } = useInspectionStats();
  const { data: inspections, isLoading: listLoading } = useInspectionsList();

  const loading = statsLoading || listLoading;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Inspections Dashboard</h1>
        <button
          onClick={() => navigate('/inspections/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          New Inspection
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
                <ClipboardList className="w-10 h-10 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-500">Total Inspections</p>
                  <h3 className="text-2xl font-bold">{stats?.total || 0}</h3>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <AlertTriangle className="w-10 h-10 text-yellow-500" />
                <div>
                  <p className="text-sm text-gray-500">Scheduled</p>
                  <h3 className="text-2xl font-bold">{stats?.scheduled || 0}</h3>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <CheckCircle className="w-10 h-10 text-green-500" />
                <div>
                  <p className="text-sm text-gray-500">Completed</p>
                  <h3 className="text-2xl font-bold">{stats?.completed || 0}</h3>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 flex items-center space-x-4">
                <Clock className="w-10 h-10 text-purple-500" />
                <div>
                  <p className="text-sm text-gray-500">Pending</p>
                  <h3 className="text-2xl font-bold">{stats?.pending || 0}</h3>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Inspections</CardTitle>
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
                    <th className="p-4">Status</th>
                    <th className="p-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(inspections || []).map((insp) => (
                    <tr key={insp.id} className="border-b hover:bg-gray-50">
                      <td className="p-4">{new Date(insp.date).toLocaleDateString()}</td>
                      <td className="p-4">{insp.mine_id}</td>
                      <td className="p-4">{insp.type}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          insp.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                          insp.status === 'OVERDUE' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {insp.status}
                        </span>
                      </td>
                      <td className="p-4">
                        <button
                          onClick={() => navigate(`/inspections/${insp.id}`)}
                          className="text-blue-600 hover:underline"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                  {(!inspections || inspections.length === 0) && (
                    <tr>
                      <td colSpan={5} className="p-12 text-center">
                        <div className="flex flex-col items-center">
                          <Inbox className="w-12 h-12 text-gray-400 mb-3" />
                          <h3 className="text-lg font-medium text-gray-900">No Inspections</h3>
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
