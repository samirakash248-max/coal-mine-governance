import { useQuery } from '@tanstack/react-query';

export interface AuditLog {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  user_id: string;
  role: string;
  before_state: any;
  after_state: any;
  timestamp: string;
  user_name?: string;
}

export function useAudit(entityType: string, entityId: string) {
  return useQuery<AuditLog[]>({
    queryKey: ['audit', entityType, entityId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      const res = await fetch(`/api/v1/audit/${entityType}/${entityId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch audit logs');
      return res.json();
    },
    enabled: !!entityType && !!entityId,
  });
}
