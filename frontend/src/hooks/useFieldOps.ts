import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface FieldEvent {
  id?: string;
  type: 'INCIDENT' | 'NEAR_MISS' | 'HAZARD_OBSERVATION' | 'UNSAFE_CONDITION';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  is_anonymous: boolean;
  created_at?: string;
}

export interface CorrectiveAction {
  id: string;
  title: string;
  description: string;
  status: 'OPEN' | 'ASSIGNED' | 'IN_PROGRESS' | 'EVIDENCE_SUBMITTED' | 'UNDER_VERIFICATION' | 'RESOLVED' | 'CLOSED';
  priority: string;
  due_date: string;
}

export interface FieldEventStats {
  total_events: number;
  near_misses: number;
  incidents: number;
  critical_hazards: number;
}

export function useFieldEventStats() {
  return useQuery({
    queryKey: ['field', 'events', 'stats'],
    queryFn: async () => {
      const { data } = await apiClient.get<FieldEventStats>('/api/v1/field/events/stats');
      return data;
    },
    staleTime: 30 * 1000,
  });
}

export function useFieldEvents() {
  return useQuery({
    queryKey: ['field', 'events'],
    queryFn: async () => {
      const { data } = await apiClient.get<FieldEvent[]>('/api/v1/field/events');
      return data;
    },
    staleTime: 30 * 1000, // Cache for 30s
  });
}

export function useCreateFieldEvent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (newEvent: Omit<FieldEvent, 'id' | 'created_at'>) => {
      const { data } = await apiClient.post('/api/v1/field/events', newEvent);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['field', 'events'] });
    },
  });
}

export function useCorrectiveActions() {
  return useQuery({
    queryKey: ['field', 'actions'],
    queryFn: async () => {
      const { data } = await apiClient.get<CorrectiveAction[]>('/api/v1/field/actions');
      return data;
    },
    staleTime: 30 * 1000, // Cache for 30s
  });
}

export function useAIClassify() {
  return useMutation({
    mutationFn: async (text: string) => {
      const { data } = await apiClient.post('/api/v1/copilot/classify', { text });
      return data;
    },
  });
}
