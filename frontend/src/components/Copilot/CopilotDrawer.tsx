import React, { useState } from 'react';
import { X, Sparkles, Send, CheckCircle2 } from 'lucide-react';
import { clsx } from 'clsx';
import { useCopilotChat, CopilotMessage, CopilotAction } from '../../hooks/useCopilot';

interface CopilotDrawerProps {
  open: boolean;
  onClose: () => void;
}

export const CopilotDrawer: React.FC<CopilotDrawerProps> = ({ open, onClose }) => {
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [input, setInput] = useState('');
  const chatMutation = useCopilotChat();

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg = input.trim();
    const newHistory: CopilotMessage[] = [...messages, { role: 'user', content: userMsg }];
    
    setMessages(newHistory);
    setInput('');

    chatMutation.mutate(
      { message: userMsg, history: messages },
      {
        onSuccess: (data) => {
          setMessages([
            ...newHistory,
            { role: 'assistant', content: data.answer, citations: data.citations, recommended_actions: data.recommended_actions } as any
          ]);
        },
      }
    );
  };

  const handleActionExecute = (action: CopilotAction) => {
    alert(`Executing action: ${action.action}`);
  };

  return (
    <>
      {open && (
        <div 
          className="fixed inset-0 z-40 bg-graphite-950/20 backdrop-blur-sm"
          onClick={onClose}
        />
      )}
      <div className={clsx(
        "fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-xl transition-transform duration-300 ease-in-out flex flex-col",
        open ? "translate-x-0" : "translate-x-full"
      )}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-graphite-50">
          <div className="flex items-center gap-2 text-graphite-800 font-semibold">
            <Sparkles size={20} className="text-mining-amber-500" />
            Governance Copilot
          </div>
          <button onClick={onClose} className="p-1 rounded-md text-gray-500 hover:bg-gray-200">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 text-sm">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-10">
              How can I assist you with compliance and governance today?
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={clsx("flex", msg.role === 'user' ? "justify-end" : "justify-start")}>
              <div className={clsx(
                "max-w-[85%] rounded-lg px-3 py-2",
                msg.role === 'user' ? "bg-mining-amber-500 text-graphite-950" : "bg-white border border-gray-200 text-gray-800"
              )}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                {(msg as any).citations && (msg as any).citations.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {(msg as any).citations.map((c: any, idx: number) => (
                      <div key={idx} className="text-[10px] bg-gray-100 p-1.5 rounded text-gray-700 border border-gray-200 shadow-sm flex flex-col gap-0.5">
                        <span className="font-semibold text-gray-900">{c.title}</span>
                        {c.section && <span>Section: {c.section}</span>}
                        {c.page && <span>Page: {c.page}</span>}
                      </div>
                    ))}
                  </div>
                )}
                {(msg as any).recommended_actions && (msg as any).recommended_actions.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {(msg as any).recommended_actions.map((act: CopilotAction) => (
                      <div key={act.id} className="bg-graphite-50 rounded p-2 border border-graphite-200 text-xs">
                        <div className="font-semibold text-graphite-700 mb-1">{act.description}</div>
                        <button
                          onClick={() => handleActionExecute(act)}
                          className="flex items-center gap-1 bg-graphite-900 text-white px-2 py-1 rounded hover:bg-graphite-800 transition-colors"
                        >
                          <CheckCircle2 size={12} /> Approve & Execute
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {chatMutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 text-gray-500 rounded-lg px-4 py-3 text-sm flex flex-col gap-2 shadow-sm min-w-[200px]">
                <div className="flex items-center gap-2 font-medium text-graphite-700">
                  <Sparkles size={14} className="animate-pulse text-mining-amber-500" />
                  Analyzing Query
                </div>
                <div className="flex space-x-1">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-xs text-gray-400 mt-1">Qwen3-4B Local Model</span>
              </div>
            </div>
          )}
          {chatMutation.isError && (
            <div className="flex justify-start">
              <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg px-3 py-2 text-sm">
                <strong>{chatMutation.error?.message?.toLowerCase().includes('timeout') || chatMutation.error?.message?.toLowerCase().includes('network') ? 'Timeout Error:' : 'Connection Error:'}</strong> {chatMutation.error?.message?.toLowerCase().includes('timeout') || chatMutation.error?.message?.toLowerCase().includes('network') ? 'AI analysis is taking longer than expected. Please try again.' : 'The governance service is temporarily unavailable.'}
              </div>
            </div>
          )}
        </div>

        <div className="p-3 bg-white border-t border-gray-200">
          <div className="relative">
            <textarea
              className="w-full resize-none rounded-lg border border-gray-300 py-2 pl-3 pr-10 focus:outline-none focus:ring-1 focus:ring-mining-amber-500 text-sm"
              rows={2}
              placeholder="Ask about compliance status..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || chatMutation.isPending}
              className="absolute right-2 bottom-2 p-1.5 text-white bg-graphite-900 rounded-md hover:bg-graphite-800 disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

