import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { apiClient as api } from '../../api/client';

export default function InspectionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [inspection, setInspection] = useState<any>(null);
  const [findings, setFindings] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        const [inspRes, findRes, actRes] = await Promise.all([
          api.get(`/api/v1/inspections/${id}`),
          api.get(`/api/v1/inspections/${id}/findings`),
          api.get(`/api/v1/inspections/${id}/actions`)
        ]);
        setInspection(inspRes.data);
        setFindings(findRes.data);
        setActions(actRes.data);
      } catch (err: any) {
        console.error('Failed to load inspection details', err);
        setError(err.response?.data?.detail || err.message || 'Failed to load inspection details');
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchData();
  }, [id]);

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;
  if (!inspection) return <div className="p-6">Not Found</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold truncate">Inspection #{id}</h1>
        <button onClick={() => navigate('/inspections')} className="text-blue-600 hover:underline shrink-0">
          Back to List
        </button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Date</p>
              <p className="font-semibold">{inspection.date ? new Date(inspection.date).toLocaleString() : 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Mine ID</p>
              <p className="font-semibold truncate" title={inspection.mine_id}>{inspection.mine_id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Inspector</p>
              <p className="font-semibold truncate" title={inspection.inspector_id}>{inspection.inspector_id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <Badge variant={inspection.status === 'COMPLETED' ? 'default' : 'secondary'}>
                {inspection.status || 'N/A'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Findings</CardTitle>
          </CardHeader>
          <CardContent>
            {findings.length === 0 ? <p className="text-gray-500">No findings.</p> : (
              <ul className="space-y-4">
                {findings.map((f, i) => (
                  <li key={i} className="border-b pb-2">
                    <p className="font-medium">{f.type || f.category || 'Finding'}</p>
                    <p className="text-sm text-gray-600">{f.description}</p>
                    {f.severity && (
                      <Badge variant={f.severity === 'HIGH' || f.severity === 'CRITICAL' ? 'destructive' : 'secondary'} className="mt-1">
                        {f.severity}
                      </Badge>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Corrective Actions</CardTitle>
          </CardHeader>
          <CardContent>
            {actions.length === 0 ? <p className="text-gray-500">No actions recorded.</p> : (
              <ul className="space-y-4">
                {actions.map((a, i) => (
                  <li key={i} className="border-b pb-2">
                    <p className="font-medium whitespace-pre-wrap">{a.description}</p>
                    <p className="text-sm text-gray-600">Due: {a.due_date ? new Date(a.due_date).toLocaleDateString() : 'N/A'}</p>
                    {a.status && (
                      <Badge variant={a.status === 'CLOSED' ? 'default' : 'secondary'} className="mt-1">
                        {a.status}
                      </Badge>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
