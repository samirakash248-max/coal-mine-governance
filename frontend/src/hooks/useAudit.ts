import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface AuditLog {
  id: string;
  user_id: string | null;
  role: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  before_state: any;
  after_state: any;
  timestamp: string;
  hash_signature: string;
}

export function useGlobalAuditLogs(page: number, limit: number, filters?: { action?: string; entity_type?: string }) {
  return useQuery({
    queryKey: ['audit-logs', 'global', page, limit, filters],
    queryFn: async () => {
      const skip = (page - 1) * limit;
      let url = `/api/v1/audit/?skip=${skip}&limit=${limit}`;
      if (filters?.action) url += `&action=${filters.action}`;
      if (filters?.entity_type) url += `&entity_type=${filters.entity_type}`;
      
      const { data } = await apiClient.get<AuditLog[]>(url);
      return data;
    },
  });
}

export function useEntityAuditLogs(entityType: string, entityId: string) {
  return useQuery({
    queryKey: ['audit-logs', entityType, entityId],
    queryFn: async () => {
      const { data } = await apiClient.get<AuditLog[]>(`/api/v1/audit/${entityType}/${entityId}`);
      return data;
    },
    enabled: !!entityId && !!entityType,
  });
}
