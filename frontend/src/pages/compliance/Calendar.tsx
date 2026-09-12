import { useComplianceCalendar } from '../../hooks/useCompliance';
import { useMemo } from 'react';
import { Skeleton } from '../../components/ui/skeleton';
import { Inbox } from 'lucide-react';

export default function Calendar() {
  const { data: records, isLoading } = useComplianceCalendar();

  const sortedRecords = useMemo(() => {
    if (!records) return [];
    return [...records].sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
  }, [records]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLIANT':
        return <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">COMPLIANT</span>;
      case 'OVERDUE':
        return <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">OVERDUE</span>;
      case 'DUE_SOON':
        return <span className="bg-amber-100 text-amber-800 px-2 py-1 rounded-full text-xs font-medium">DUE SOON</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs font-medium">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-gray-900">Compliance Calendar</h1>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-4 font-medium">Requirement</th>
                  <th className="px-6 py-4 font-medium">Due Date</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {sortedRecords.map(record => (
                  <tr key={record.id} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{record.requirement?.title}</td>
                    <td className="px-6 py-4">{new Date(record.due_date).toLocaleDateString()}</td>
                    <td className="px-6 py-4">{getStatusBadge(record.status)}</td>
                  </tr>
                ))}
                {sortedRecords.length === 0 && (
                  <tr>
                    <td colSpan={3} className="p-12 text-center">
                      <div className="flex flex-col items-center">
                        <Inbox className="w-12 h-12 text-gray-400 mb-3" />
                        <h3 className="text-lg font-medium text-gray-900">No upcoming deadlines</h3>
                        <p className="text-gray-500 mt-1">Your compliance calendar is clear.</p>
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
