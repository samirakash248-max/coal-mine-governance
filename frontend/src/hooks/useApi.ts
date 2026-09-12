import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';
import { type AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  refetch: () => Promise<void>;
}

export function useApi<T>(url: string, options?: { immediate?: boolean }): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: options?.immediate !== false,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await apiClient.get<T>(url);
      setState({ data: response.data, loading: false, error: null });
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      const message = axiosError.response?.data?.detail || axiosError.message || 'An error occurred';
      setState({ data: null, loading: false, error: message });
    }
  }, [url]);

  useEffect(() => {
    if (options?.immediate !== false) {
      fetchData();
    }
  }, [fetchData, options?.immediate]);

  return { ...state, refetch: fetchData };
}
