import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Skeleton } from '../../components/ui/skeleton';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Shield, ChevronLeft, ChevronRight, Hash } from 'lucide-react';
import { useGlobalAuditLogs, AuditLog } from '../../hooks/useAudit';

export default function AuditTrail() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<{ action?: string; entity_type?: string }>({});
  
  const limit = 20;
  const { data: logs, isLoading, isError, refetch } = useGlobalAuditLogs(page, limit, filters);

  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  const handleFilterChange = (key: 'action' | 'entity_type', value: string) => {
    setFilters(prev => ({ ...prev, [key]: value || undefined }));
    setPage(1); // Reset to first page on filter change
    setSelectedLog(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Audit Trail</h1>
          <p className="text-gray-500">Immutable chronological record of governance decisions and events.</p>
        </div>
      </div>

      <div className="flex gap-4 mb-4">
        <select 
          className="border border-gray-300 rounded-md text-sm p-2 w-48"
          value={filters.action || ''}
          onChange={(e) => handleFilterChange('action', e.target.value)}
        >
          <option value="">All Actions</option>
          <option value="CREATE">CREATE</option>
          <option value="UPDATE">UPDATE</option>
          <option value="REVIEW">REVIEW</option>
          <option value="APPROVE">APPROVE</option>
          <option value="ESCALATE">ESCALATE</option>
        </select>

        <select 
          className="border border-gray-300 rounded-md text-sm p-2 w-48"
          value={filters.entity_type || ''}
          onChange={(e) => handleFilterChange('entity_type', e.target.value)}
        >
          <option value="">All Entities</option>
          <option value="SafetyEvent">SafetyEvent</option>
          <option value="CorrectiveAction">CorrectiveAction</option>
          <option value="Report">Report</option>
          <option value="Document">Document</option>
        </select>
        
        <Button variant="outline" onClick={() => { setFilters({}); setPage(1); }}>Clear Filters</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-500">
                  <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                    <tr>
                      <th className="px-4 py-3">Timestamp</th>
                      <th className="px-4 py-3">Action</th>
                      <th className="px-4 py-3">Actor</th>
                      <th className="px-4 py-3">Entity</th>
                      <th className="px-4 py-3 text-right">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      [...Array(10)].map((_, i) => (
                        <tr key={i} className="border-b">
                          <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                          <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                          <td className="px-4 py-3"><Skeleton className="h-4 w-20" /></td>
                          <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                          <td className="px-4 py-3 text-right"><Skeleton className="h-6 w-16 inline-block" /></td>
                        </tr>
                      ))
                    ) : isError ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-red-500">
                          Failed to load audit trail. <Button variant="link" onClick={() => refetch()}>Retry</Button>
                        </td>
                      </tr>
                    ) : !logs || logs.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                          No audit records found matching your filters.
                        </td>
                      </tr>
                    ) : (
                      logs.map((log) => (
                        <tr 
                          key={log.id} 
                          className={`border-b hover:bg-gray-50 cursor-pointer ${selectedLog?.id === log.id ? 'bg-blue-50' : ''}`}
                          onClick={() => setSelectedLog(log)}
                        >
                          <td className="px-4 py-3 whitespace-nowrap">{new Date(log.timestamp).toLocaleString()}</td>
                          <td className="px-4 py-3 font-medium text-gray-900">{log.action}</td>
                          <td className="px-4 py-3">
                            {log.role === 'AI_AGENT' ? (
                              <Badge variant="outline" className="bg-primary-50 text-primary-700 border-primary-200">AI SYSTEM</Badge>
                            ) : (
                              log.role || 'SYSTEM'
                            )}
                          </td>
                          <td className="px-4 py-3 font-mono text-xs text-gray-600">
                            {log.entity_type}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <Button size="sm" variant="ghost">View</Button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
                <span className="text-sm text-gray-500">Page {page}</span>
                <div className="space-x-2">
                  <Button size="sm" variant="outline" disabled={page === 1} onClick={() => setPage(p => Math.max(1, p - 1))}>
                    <ChevronLeft className="w-4 h-4 mr-1" /> Prev
                  </Button>
                  <Button size="sm" variant="outline" disabled={!logs || logs.length < limit} onClick={() => setPage(p => p + 1)}>
                    Next <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1">
          {selectedLog ? (
            <Card className="sticky top-6">
              <CardHeader className="bg-gray-50 border-b border-gray-100 pb-4">
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="outline">{selectedLog.action}</Badge>
                  <div className="text-xs text-gray-500">{new Date(selectedLog.timestamp).toLocaleString()}</div>
                </div>
                <CardTitle className="text-lg">Event Record</CardTitle>
                <div className="text-xs font-mono text-gray-500 break-all flex items-center gap-1 mt-1">
                  <Hash className="w-3 h-3" /> {selectedLog.id}
                </div>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                <div>
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Actor</div>
                  <div className="text-sm font-medium">
                    {selectedLog.role === 'AI_AGENT' ? (
                      <span className="text-primary-600 flex items-center gap-1">AI Recommendation System</span>
                    ) : (
                      <span>Human Action ({selectedLog.role || 'SYSTEM'})</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5 break-all">{selectedLog.user_id || 'System Process'}</div>
                </div>
                
                <div>
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Entity Affected</div>
                  <div className="text-sm font-medium">{selectedLog.entity_type}</div>
                  <div className="text-xs font-mono text-gray-500 mt-0.5 break-all">{selectedLog.entity_id}</div>
                </div>

                {selectedLog.before_state && (
                  <div>
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Previous State</div>
                    <div className="bg-gray-100 p-2 rounded text-xs font-mono text-gray-600 max-h-32 overflow-y-auto">
                      {JSON.stringify(selectedLog.before_state, null, 2)}
                    </div>
                  </div>
                )}

                {selectedLog.after_state && (
                  <div>
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-1">New State / Result</div>
                    <div className="bg-gray-100 p-2 rounded text-xs font-mono text-gray-600 max-h-32 overflow-y-auto">
                      {JSON.stringify(selectedLog.after_state, null, 2)}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-100">
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Cryptographic Signature</div>
                  <div className="text-[10px] font-mono text-gray-400 break-all bg-gray-50 p-2 rounded border border-gray-100">
                    {selectedLog.hash_signature}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center bg-gray-50 border-dashed min-h-[400px]">
              <div className="text-center text-gray-500">
                <Shield className="h-12 w-12 mx-auto text-gray-300 mb-2" />
                <p>Select an audit event to view detailed record.</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

