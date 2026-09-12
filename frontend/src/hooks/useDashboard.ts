import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

interface DashboardSummary {
  total_mines: number;
  compliance_percentage: number;
  overdue_count: number;
  due_soon_count: number;
  open_findings_count?: number;
  critical_findings_count?: number;
  open_near_misses_count?: number;
  incidents_count?: number;
  overdue_actions_count?: number;
}

export function useDashboardSummary() {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardSummary>('/api/v1/dashboard/summary');
      return data;
    },
    staleTime: 30 * 1000, // Cache for 30s — prevents duplicate requests on re-navigation
  });
}
