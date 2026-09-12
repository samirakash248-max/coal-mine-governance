import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface EnvReading {
  timestamp: string;
  air_quality_index: number;
  dust_pm10: number;
  water_ph: number;
}

export interface ProductionData {
  date: string;
  target_tons: number;
  actual_tons: number;
}

export interface Contractor {
  id: string;
  name: string;
  workers_count: number;
  status: string;
}

export function useOperations(mineId: string) {
  
  const envQuery = useQuery({
    queryKey: ['operations', mineId, 'environment'],
    queryFn: async () => {
      const { data } = await apiClient.get<EnvReading[]>(`/api/v1/operations/environment?mine_id=${mineId}`);
      return data;
    },
    enabled: !!mineId,
  });

  const prodQuery = useQuery({
    queryKey: ['operations', mineId, 'production'],
    queryFn: async () => {
      const { data } = await apiClient.get<ProductionData[]>(`/api/v1/operations/production?mine_id=${mineId}`);
      return data;
    },
    enabled: !!mineId,
  });

  const contractorsQuery = useQuery({
    queryKey: ['operations', mineId, 'contractors'],
    queryFn: async () => {
      const { data } = await apiClient.get<Contractor[]>(`/api/v1/operations/contractors?mine_id=${mineId}`);
      return data;
    },
    enabled: !!mineId,
  });

  return {
    environment: envQuery.data,
    isEnvLoading: envQuery.isLoading,
    production: prodQuery.data,
    isProdLoading: prodQuery.isLoading,
    contractors: contractorsQuery.data,
    isContractorsLoading: contractorsQuery.isLoading,
  };
}
