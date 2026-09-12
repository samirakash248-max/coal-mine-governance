import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface InspectionStats {
  total: number;
  completed: number;
  pending: number;
  scheduled: number;
  compliance_percentage: number;
}

export interface Inspection {
  id: string;
  mine_id: string;
  type: string;
  date: string;
  status: string;
  inspector_id: string;
}

export function useInspectionStats() {
  return useQuery({
    queryKey: ['inspections', 'stats'],
    queryFn: async () => {
      const { data } = await apiClient.get<InspectionStats>('/api/v1/inspections/stats');
      return data;
    },
    staleTime: 30 * 1000,
  });
}

export function useInspectionsList() {
  return useQuery({
    queryKey: ['inspections', 'list'],
    queryFn: async () => {
      const { data } = await apiClient.get<Inspection[]>('/api/v1/inspections/');
      return data;
    },
    staleTime: 30 * 1000,
  });
}
