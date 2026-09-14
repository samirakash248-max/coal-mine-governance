import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient as api } from '../api/client';

// Types
export interface Document {
  id: string;
  title: string;
  document_number: string;
  category: string;
  issue_date: string;
  expiry_date: string;
  status: string;
}

export interface VerifyDocumentPayload {
  title: string;
  document_number: string;
  category: string;
  issue_date: string;
  expiry_date: string;
}

export const useDocuments = () => {
  return useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const { data } = await api.get<Document[]>('/api/v1/documents');
      return data;
    },
  });
};

export const useDocument = (id: string) => {
  return useQuery({
    queryKey: ['documents', id],
    queryFn: async () => {
      const { data } = await api.get<Document>(`/api/v1/documents/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await api.post<Document>('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

export const useVerifyDocument = (id: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: VerifyDocumentPayload) => {
      const { data } = await api.put<Document>(`/api/v1/documents/${id}/verify`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

export const useSearchDocuments = () => {
  return useMutation({
    mutationFn: async (query: string) => {
      const { data } = await api.post('/api/v1/documents/search', { query });
      return data;
    },
  });
};
