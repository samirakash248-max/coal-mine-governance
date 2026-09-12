import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { apiClient as api } from '../../api/client';


export default function CreateInspection() {
  const navigate = useNavigate();
  
  const [mines, setMines] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    mine_id: '',
    type: 'ROUTINE',
    date: '',
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
      const payload = {
        ...formData,
        date: formData.date ? new Date(formData.date).toISOString() : new Date().toISOString(),
        checklist_data: {}
      };
      await api.post('/api/v1/inspections/', payload);
      navigate('/inspections');
    } catch (error) {
      console.error('Failed to create inspection', error);
      alert('Error creating inspection');
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Schedule New Inspection</CardTitle>
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
              <label className="block text-sm font-medium mb-1">Type</label>
              <select
                className="w-full p-2 border rounded-md"
                value={formData.type}
                onChange={e => setFormData({...formData, type: e.target.value})}
              >
                <option value="ROUTINE">Routine</option>
                <option value="SURPRISE">Surprise</option>
                <option value="FOLLOWUP">Follow-up</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Date</label>
              <input
                type="date"
                required
                className="w-full p-2 border rounded-md"
                value={formData.date}
                onChange={e => setFormData({...formData, date: e.target.value})}
              />
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <button
                type="button"
                onClick={() => navigate('/inspections')}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Create
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
