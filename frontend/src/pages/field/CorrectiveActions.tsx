import { useCorrectiveActions } from '../../hooks/useFieldOps';
import { Inbox } from 'lucide-react';
import { Skeleton } from '../../components/ui/skeleton';

export default function CorrectiveActions() {
  const { data: actions, isLoading } = useCorrectiveActions();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPEN': return 'bg-red-100 text-red-800';
      case 'ASSIGNED': return 'bg-primary-100 text-primary-800';
      case 'IN_PROGRESS': return 'bg-amber-100 text-amber-800';
      case 'EVIDENCE_SUBMITTED': return 'bg-emerald-100 text-emerald-800';
      case 'UNDER_VERIFICATION': return 'bg-amber-100 text-amber-800';
      case 'RESOLVED': return 'bg-green-100 text-green-800';
      case 'CLOSED': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Corrective Actions</h1>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-4 font-medium text-left">Action Details</th>
                  <th className="px-6 py-4 font-medium text-left">Status</th>
                  <th className="px-6 py-4 font-medium text-left">Due Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {actions?.map(action => (
                  <tr key={action.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <p className="text-gray-900 font-medium">{action.description}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${getStatusColor(action.status)}`}>
                        {action.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {new Date(action.due_date).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {!actions?.length && (
                  <tr>
                    <td colSpan={4} className="p-12 text-center">
                      <div className="flex flex-col items-center">
                        <Inbox className="w-12 h-12 text-gray-400 mb-3" />
                        <h3 className="text-lg font-medium text-gray-900">No Actions Found</h3>
                        <p className="text-gray-500 mt-1">There are currently no corrective actions to display.</p>
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
