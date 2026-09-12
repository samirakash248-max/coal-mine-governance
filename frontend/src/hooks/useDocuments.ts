import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

// Types
export interface Document {
  id: string;
  title: string;
  documentNumber: string;
  category: string;
  issueDate: string;
  expiryDate: string;
  status: string;
}

export interface VerifyDocumentPayload {
  title: string;
  documentNumber: string;
  category: string;
  issueDate: string;
  expiryDate: string;
}

export const useDocuments = () => {
  return useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const { data } = await api.get<Document[]>('/documents');
      return data;
    },
  });
};

export const useDocument = (id: string) => {
  return useQuery({
    queryKey: ['documents', id],
    queryFn: async () => {
      const { data } = await api.get<Document>(`/documents/${id}`);
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
      const { data } = await api.post<Document>('/documents/upload', formData, {
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
      const { data } = await api.put<Document>(`/documents/${id}/verify`, payload);
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
      const { data } = await api.post('/documents/search', { query });
      return data;
    },
  });
};
