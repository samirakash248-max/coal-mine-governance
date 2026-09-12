import { useDashboardSummary } from '../hooks/useDashboard';
import { useComplianceCalendar } from '../hooks/useCompliance';
import { Skeleton } from '../components/ui/skeleton';
import { Inbox } from 'lucide-react';

export default function Dashboard() {
  const { data: summary, isLoading: isSummaryLoading } = useDashboardSummary();
  const { data: calendar, isLoading: isCalendarLoading } = useComplianceCalendar();

  const urgentRecords = calendar?.filter(r => r.status === 'OVERDUE' || r.status === 'DUE_SOON') || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      
      {isSummaryLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <Skeleton className="h-4 w-20 mb-3" />
              <Skeleton className="h-8 w-12" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Total Mines</h3>
            <p className="text-3xl font-bold mt-2">{summary?.total_mines ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Compliance %</h3>
            <p className="text-3xl font-bold mt-2">{summary?.compliance_percentage ?? 0}%</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Overdue</h3>
            <p className="text-3xl font-bold mt-2 text-red-600">{summary?.overdue_count ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Due Soon</h3>
            <p className="text-3xl font-bold mt-2 text-amber-600">{summary?.due_soon_count ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-red-200 shadow-sm">
            <h3 className="text-sm font-medium text-red-700">Critical Findings</h3>
            <p className="text-3xl font-bold mt-2 text-red-700">{summary?.critical_findings_count ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Open Findings</h3>
            <p className="text-3xl font-bold mt-2 text-gray-900">{summary?.open_findings_count ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-amber-200 shadow-sm">
            <h3 className="text-sm font-medium text-amber-700">Open Near Misses</h3>
            <p className="text-3xl font-bold mt-2 text-amber-700">{summary?.open_near_misses_count ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-orange-200 shadow-sm">
            <h3 className="text-sm font-medium text-orange-700">Incidents</h3>
            <p className="text-3xl font-bold mt-2 text-orange-700">{summary?.incidents_count ?? 0}</p>
          </div>
          <div className="bg-white p-6 rounded-xl border border-red-200 shadow-sm">
            <h3 className="text-sm font-medium text-red-700">Overdue Actions</h3>
            <p className="text-3xl font-bold mt-2 text-red-700">{summary?.overdue_actions_count ?? 0}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Urgent Compliance Records</h2>
        </div>
        {isCalendarLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-6 py-3">Title</th>
                  <th className="px-6 py-3">Due Date</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {urgentRecords.map(record => (
                  <tr key={record.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{record.requirement?.title}</td>
                    <td className="px-6 py-4">{new Date(record.due_date).toLocaleDateString()}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        record.status === 'OVERDUE' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {record.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {urgentRecords.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center">
                        <Inbox className="w-12 h-12 text-gray-400 mb-3" />
                        <h3 className="text-lg font-medium text-gray-900">No urgent records</h3>
                        <p className="text-gray-500 mt-1">All compliance records are up to date.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
