import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface ComplianceRecord {
  id: string;
  due_date: string;
  status: 'COMPLIANT' | 'OVERDUE' | 'DUE_SOON' | 'PENDING';
  requirement: {
    title: string;
    description: string;
  };
}

export function useComplianceCalendar() {
  return useQuery({
    queryKey: ['compliance', 'calendar'],
    queryFn: async () => {
      const { data } = await apiClient.get<ComplianceRecord[]>('/api/v1/compliance/records/calendar');
      return data;
    },
    staleTime: 60 * 1000, // Cache compliance data for 60s
  });
}
