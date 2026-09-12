import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface CopilotMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CopilotChatPayload {
  message: string;
  history?: CopilotMessage[];
}

export interface CopilotCitation {
  title: string;
  url?: string;
  snippet?: string;
}

export interface CopilotAction {
  id: string;
  action: string;
  description: string;
}

export interface CopilotChatResponse {
  answer: string;
  citations: CopilotCitation[];
  recommended_actions: CopilotAction[];
}

export const useCopilotChat = () => {
  return useMutation<CopilotChatResponse, Error, CopilotChatPayload>({
    mutationFn: async (payload) => {
      const response = await apiClient.post('/api/v1/copilot/chat', payload);
      return response.data;
    },
  });
};

export interface DailyBriefResponse {
  critical_issues: any[];
  attention_items: any[];
  positive_developments: any[];
  recommendations: any[];
}

export const useDailyBrief = () => {
  return useQuery<DailyBriefResponse, Error>({
    queryKey: ['daily-brief'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/copilot/daily-brief');
      return response.data;
    },
  });
};
