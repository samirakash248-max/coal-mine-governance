import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { apiClient as api } from '../../api/client';

export default function EventDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const res = await api.get(`/field/events/${id}`);
        setEvent(res.data);
      } catch (error) {
        console.error('Failed to load event details', error);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchEvent();
  }, [id]);

  if (loading) return <div className="p-6">Loading...</div>;
  if (!event) return <div className="p-6">Not Found</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Event #{id}</h1>
        <button onClick={() => navigate('/safety')} className="text-blue-600 hover:underline">
          Back to List
        </button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Event Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
            <div>
              <p className="text-sm text-gray-500">Date</p>
              <p className="font-semibold">{event.date}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Location</p>
              <p className="font-semibold">{event.location}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Type</p>
              <p className="font-semibold">{event.type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Severity</p>
              <Badge variant={event.severity === 'HIGH' ? 'destructive' : (event.severity === 'MEDIUM' ? 'destructive' : 'default')}>
                {event.severity}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-500">Reporter</p>
              <p className="font-semibold">{event.reporter}</p>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Description</p>
            <p className="bg-gray-50 p-4 rounded-md">{event.description}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
