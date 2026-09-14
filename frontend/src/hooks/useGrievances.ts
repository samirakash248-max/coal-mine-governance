import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface Grievance {
  id: string;
  mine_id: string;
  title: string;
  description: string;
  status: string;
  category?: string;
  priority?: string;
  ai_suggestions?: {
    suggested_category: string;
    suggested_priority: string;
    reasoning: string;
  };
  created_at: string;
  updated_at: string;
}

export function useGrievances() {
  const queryClient = useQueryClient();

  const { data: grievances, isLoading, isError } = useQuery({
    queryKey: ['grievances'],
    queryFn: async () => {
      const { data } = await apiClient.get<Grievance[]>('/api/v1/grievances');
      return data;
    },
  });

  const createGrievance = useMutation({
    mutationFn: async (payload: { title: string; description: string; mine_id?: string }) => {
      const { data } = await apiClient.post<Grievance>('/api/v1/grievances', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grievances'] });
    },
  });

  const applyAiSuggestions = useMutation({
    mutationFn: async (payload: { id: string; category: string }) => {
      const { data } = await apiClient.put<Grievance>(`/api/v1/grievances/${payload.id}/apply-ai`, {
        category: payload.category
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grievances'] });
    },
  });

  return {
    grievances,
    isLoading,
    isError,
    createGrievance,
    applyAiSuggestions,
  };
}
