import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';

const regionalData = [
  { region: 'North', compliance: 85, target: 90 },
  { region: 'South', compliance: 92, target: 90 },
  { region: 'East', compliance: 78, target: 90 },
  { region: 'West', compliance: 95, target: 90 },
];

const incidentData = [
  { month: 'Jan', incidents: 4, nearMisses: 10 },
  { month: 'Feb', incidents: 3, nearMisses: 12 },
  { month: 'Mar', incidents: 5, nearMisses: 8 },
  { month: 'Apr', incidents: 2, nearMisses: 15 },
  { month: 'May', incidents: 1, nearMisses: 18 },
  { month: 'Jun', incidents: 3, nearMisses: 11 },
];

export default function ExecutiveDashboard() {
  const navigate = useNavigate();

  const handleBarClick = (data: any) => {
    // Drill-down logic: navigate to /mines when a bar is clicked
    if (data && data.region) {
      navigate(`/mines?region=${data.region.toLowerCase()}`);
    } else {
      navigate('/mines');
    }
  };

  const handleLineClick = (data: any) => {
    if (data && data.activePayload && data.activePayload.length > 0) {
      navigate('/reports');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">Executive Dashboard</h1>
        <p className="text-gray-500">Overview of regional compliance and incident trends.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Regional Compliance Comparison</CardTitle>
            <CardDescription>Click on a bar to view regional mines</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regionalData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="region" />
                <YAxis />
                <RechartsTooltip cursor={{fill: 'transparent'}} />
                <Legend />
                <Bar 
                  dataKey="compliance" 
                  name="Compliance %" 
                  fill="#f59e0b" 
                  radius={[4, 4, 0, 0]} 
                  onClick={handleBarClick}
                  cursor="pointer"
                />
                <Bar 
                  dataKey="target" 
                  name="Target %" 
                  fill="#94a3b8" 
                  radius={[4, 4, 0, 0]} 
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Incident vs Near Miss Trends</CardTitle>
            <CardDescription>Click on a data point to view reports</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={incidentData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }} onClick={handleLineClick}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="incidents" 
                  name="Incidents" 
                  stroke="#ef4444" 
                  strokeWidth={3}
                  activeDot={{ r: 8, cursor: 'pointer' }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="nearMisses" 
                  name="Near Misses" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  activeDot={{ r: 8, cursor: 'pointer' }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
