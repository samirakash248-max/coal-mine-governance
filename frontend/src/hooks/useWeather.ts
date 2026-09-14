import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export function useWeatherSummary() {
  return useQuery({
    queryKey: ['weather-summary'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/v1/weather/summary');
      return data;
    }
  });
}
