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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [inspRes, findRes, actRes] = await Promise.all([
          api.get(`/inspections/${id}`),
          api.get(`/inspections/${id}/findings`),
          api.get(`/inspections/${id}/actions`)
        ]);
        setInspection(inspRes.data);
        setFindings(findRes.data);
        setActions(actRes.data);
      } catch (error) {
        console.error('Failed to load inspection details', error);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchData();
  }, [id]);

  if (loading) return <div className="p-6">Loading...</div>;
  if (!inspection) return <div className="p-6">Not Found</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inspection #{id}</h1>
        <button onClick={() => navigate('/inspections')} className="text-blue-600 hover:underline">
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
              <p className="font-semibold">{inspection.date}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Mine ID</p>
              <p className="font-semibold">{inspection.mineId}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Inspector</p>
              <p className="font-semibold">{inspection.inspector}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <Badge variant={inspection.status === 'COMPLETED' ? 'default' : 'default'}>
                {inspection.status}
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
                    <p className="font-medium">{f.title}</p>
                    <p className="text-sm text-gray-600">{f.description}</p>
                    <Badge variant={f.severity === 'HIGH' ? 'destructive' : 'destructive'} className="mt-1">
                      {f.severity}
                    </Badge>
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
                    <p className="font-medium">{a.title}</p>
                    <p className="text-sm text-gray-600">Due: {a.dueDate}</p>
                    <Badge variant={a.status === 'CLOSED' ? 'default' : 'default'} className="mt-1">
                      {a.status}
                    </Badge>
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
