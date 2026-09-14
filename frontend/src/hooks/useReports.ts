import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export type ReportStatus = 'DRAFT' | 'REVIEWED' | 'APPROVED';
export type ReportType = 'COMPLIANCE' | 'INCIDENT' | 'ENVIRONMENTAL' | 'CONTRACTOR' | 'GOVERNANCE';

export interface Report {
  id: string;
  mine_id: string;
  title: string;
  type: ReportType;
  status: ReportStatus;
  data_snapshot: any;
  created_at: string;
}

export function useReports() {
  const queryClient = useQueryClient();

  const { data: reports, isLoading, isError } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const { data } = await apiClient.get<Report[]>('/api/v1/reports');
      return data;
    },
  });

  const updateStatus = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: ReportStatus }) => {
      const { data } = await apiClient.put<Report>(`/api/v1/reports/${id}/status`, { status });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });

  return {
    reports,
    isLoading,
    isError,
    updateStatus,
  };
}
