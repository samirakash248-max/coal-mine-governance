import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
 // assuming this exists, wait I'll define a local interface

export interface RiskEvent {
  id: string;
  mine_id: string;
  type: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  is_ai_overridden: boolean;
  risk_score: number | null;
  risk_level: string | null;
  risk_factors: Record<string, any> | null;
  created_at: string;
}

export function useHighRiskCases() {
  return useQuery({
    queryKey: ['risk-cases', 'high'],
    queryFn: async () => {
      const { data } = await apiClient.get<RiskEvent[]>('/api/v1/analytics/risk/cases');
      return data;
    },
  });
}

