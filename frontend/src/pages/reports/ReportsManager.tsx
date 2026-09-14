import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { Skeleton } from '../../components/ui/skeleton';
import { FileText, Download, Check, Eye } from 'lucide-react';
import { useReports, ReportStatus } from '../../hooks/useReports';

export default function ReportsManager() {
  const { reports, isLoading, isError, updateStatus } = useReports();

  const handleReview = (id: string) => {
    updateStatus.mutate({ id, status: 'REVIEWED' });
  };

  const handleApprove = (id: string) => {
    updateStatus.mutate({ id, status: 'APPROVED' });
  };

  const handleExport = (id: string) => {
    alert(`Exporting report ${id} started...`);
  };

  const getStatusBadgeClasses = (status: ReportStatus) => {
    switch (status) {
      case 'DRAFT': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'REVIEWED': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'APPROVED': return 'bg-green-100 text-green-800 border-green-200';
      
      default: return '';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Reports Manager</h1>
          <p className="text-gray-500">Manage and export compliance and safety reports.</p>
        </div>
        <Button variant="outline" onClick={() => alert('Exporting all to CSV')}>
          <Download className="mr-2 h-4 w-4" />
          Export All (CSV)
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Reports</CardTitle>
          <CardDescription>Generated documents ready for review</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : isError ? (
            <div className="text-red-500 py-6 text-center">
              Failed to load reports from the server.
            </div>
          ) : !reports || reports.length === 0 ? (
            <div className="text-gray-500 py-8 flex flex-col items-center">
              <FileText className="h-12 w-12 text-gray-300 mb-3" />
              <p>No reports found in the database.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                  <tr>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Title</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((report) => (
                    <tr key={report.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900 flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-400" />
                        {report.type}
                      </td>
                      <td className="px-4 py-3">{report.title}</td>
                      <td className="px-4 py-3">{new Date(report.created_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className={getStatusBadgeClasses(report.status)}>
                          {report.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right space-x-2">
                        {report.status === 'DRAFT' && (
                          <Button size="sm" variant="outline" onClick={() => handleReview(report.id)}>
                            <Eye className="h-3 w-3 mr-1" /> Review
                          </Button>
                        )}
                        {report.status === 'REVIEWED' && (
                          <Button size="sm" variant="default" className="bg-green-600 hover:bg-green-700 text-white" onClick={() => handleApprove(report.id)}>
                            <Check className="h-3 w-3 mr-1" /> Approve
                          </Button>
                        )}
                        <Button size="sm" variant="ghost" onClick={() => handleExport(report.id)} title="Export PDF/CSV">
                          <Download className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

