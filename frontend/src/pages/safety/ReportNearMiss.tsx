import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { apiClient as api } from '../../api/client';


export default function ReportNearMiss() {
  const navigate = useNavigate();
  
  const [mines, setMines] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    mine_id: '',
    type: 'NEAR_MISS',
    location_details: '',
    description: '',
    severity: 'LOW',
    is_anonymous: false
  });

  useEffect(() => {
    const fetchMines = async () => {
      try {
        const res = await api.get('/api/v1/hierarchy/mines');
        setMines(res.data);
        if (res.data.length > 0) {
          setFormData(prev => ({ ...prev, mine_id: res.data[0].id }));
        }
      } catch (err) {
        console.error('Failed to fetch mines', err);
      }
    };
    fetchMines();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/field/events', formData);
      navigate('/safety');
    } catch (error) {
      console.error('Failed to report near miss', error);
      alert('Error reporting event');
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Report Near Miss</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Mine/Site</label>
              <select
                required
                className="w-full p-2 border rounded-md"
                value={formData.mine_id}
                onChange={e => setFormData({...formData, mine_id: e.target.value})}
              >
                {mines.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Exact Area/Location</label>
              <input
                type="text"
                required
                className="w-full p-2 border rounded-md"
                value={formData.location_details}
                onChange={e => setFormData({...formData, location_details: e.target.value})}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Severity</label>
              <select
                className="w-full p-2 border rounded-md"
                value={formData.severity}
                onChange={e => setFormData({...formData, severity: e.target.value})}
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                required
                rows={4}
                className="w-full p-2 border rounded-md"
                value={formData.description}
                onChange={e => setFormData({...formData, description: e.target.value})}
              ></textarea>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="anonymous"
                checked={formData.is_anonymous}
                onChange={e => setFormData({...formData, is_anonymous: e.target.checked})}
              />
              <label htmlFor="anonymous" className="text-sm font-medium">Report Anonymously</label>
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <button
                type="button"
                onClick={() => navigate('/safety')}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Submit Report
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
