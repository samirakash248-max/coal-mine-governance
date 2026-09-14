import { useQuery, useMutation } from '@tanstack/react-query';
import { aiApiClient } from '../api/client';

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
      // Use aiApiClient for longer timeout tolerance
      const response = await aiApiClient.post('/api/v1/copilot/chat', payload);
      return response.data;
    },
    retry: false, // Do not blindly retry expensive mutations
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
      // Use aiApiClient for longer timeout tolerance
      const response = await aiApiClient.get('/api/v1/copilot/daily-brief');
      return response.data;
    },
    retry: false, // Prevent React Query from hammering the backend on timeout
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes to avoid redundant heavy generation
  });
};

