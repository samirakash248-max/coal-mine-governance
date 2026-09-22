import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useAuth } from '../providers/AuthProvider';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  permissions: string[];
}

export const useUser = () => {
  const { isAuthenticated } = useAuth();

  return useQuery<UserProfile, Error>({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/auth/me');
      return response.data;
    },
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // Cache user profile for 5 minutes
  });
};
