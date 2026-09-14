
import { useEntityAuditLogs as useAudit, AuditLog } from '../hooks/useAudit';
import { clsx } from 'clsx';
import { Activity, CheckCircle, AlertTriangle, Edit2, PlusCircle } from 'lucide-react';

interface AuditTimelineProps {
  entityType: string;
  entityId: string;
}

export function AuditTimeline({ entityType, entityId }: AuditTimelineProps) {
  const { data: logs = [], isLoading, error } = useAudit(entityType, entityId);

  if (isLoading) {
    return <div className="p-4 text-sm text-gray-500 animate-pulse">Loading audit history...</div>;
  }

  if (error) {
    return <div className="p-4 text-sm text-red-500">Failed to load audit history.</div>;
  }

  if (logs.length === 0) {
    return <div className="p-4 text-sm text-gray-500">No activity recorded yet.</div>;
  }

  const getActionIcon = (action: string) => {
    switch (action?.toUpperCase()) {
      case 'CREATE':
        return <PlusCircle size={16} className="text-green-500" />;
      case 'UPDATE':
        return <Edit2 size={16} className="text-primary-500" />;
      case 'ESCALATE':
        return <AlertTriangle size={16} className="text-red-500" />;
      case 'VERIFY':
        return <CheckCircle size={16} className="text-emerald-500" />;
      default:
        return <Activity size={16} className="text-gray-500" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action?.toUpperCase()) {
      case 'CREATE': return 'bg-green-100 border-green-200';
      case 'UPDATE': return 'bg-primary-100 border-primary-200';
      case 'ESCALATE': return 'bg-red-100 border-red-200';
      case 'VERIFY': return 'bg-emerald-100 border-emerald-200';
      default: return 'bg-gray-100 border-gray-200';
    }
  };

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {logs.map((log: AuditLog, logIdx: number) => (
          <li key={log.id || logIdx}>
            <div className="relative pb-8">
              {logIdx !== logs.length - 1 ? (
                <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
              ) : null}
              <div className="relative flex space-x-3">
                <div>
                  <span className={clsx("h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white", getActionColor(log.action))}>
                    {getActionIcon(log.action)}
                  </span>
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                  <div>
                    <p className="text-sm text-gray-500">
                      <span className="font-medium text-gray-900">{log.action}</span> by{' '}
                      <span className="font-medium text-gray-900">
                        {log.user_id} {log.role && `(${log.role})`}
                      </span>
                    </p>
                  </div>
                  <div className="whitespace-nowrap text-right text-sm text-gray-500">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : ''}
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

