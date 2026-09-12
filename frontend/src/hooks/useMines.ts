import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface Mine {
  id: string;
  name: string;
  location: string;
  status: string;
}

export function useMines() {
  return useQuery({
    queryKey: ['mines'],
    queryFn: async () => {
      const { data } = await apiClient.get<Mine[]>('/api/v1/hierarchy/mines');
      return data;
    },
    staleTime: 5 * 60 * 1000, // Mine hierarchy is stable — cache 5 min
  });
}

export function useMine(id: string) {
  return useQuery({
    queryKey: ['mines', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Mine>(`/api/v1/hierarchy/mines/${id}`);
      return data;
    },
    enabled: !!id,
  });
}
