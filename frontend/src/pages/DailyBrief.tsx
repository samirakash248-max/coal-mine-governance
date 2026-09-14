import { useState, useEffect } from 'react';
import { AlertTriangle, Info, CheckCircle, Lightbulb, RefreshCw, Loader2, AlertCircle } from 'lucide-react';
import { useDailyBrief } from '../hooks/useCopilot';
import { Button } from '../components/ui/button';

export default function DailyBrief() {
  const { data, isLoading, isError, refetch, error } = useDailyBrief();
  const [loadingStep, setLoadingStep] = useState(0);

  const loadingMessages = [
    "Compiling daily governance data...",
    "AI is analyzing recent safety events...",
    "Extracting critical compliance issues...",
    "Generating actionable recommendations...",
    "Almost finished..."
  ];

  useEffect(() => {
    let interval: any;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < loadingMessages.length - 1 ? prev + 1 : prev));
      }, 5000); // Change message every 5 seconds
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-500 space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-lg font-medium">{loadingMessages[loadingStep]}</p>
        <p className="text-sm text-gray-400 max-w-md text-center">
          This operation requires deep context analysis and may take up to a minute.
        </p>
      </div>
    );
  }

  if (isError || !data) {
    const isTimeout = error?.message?.toLowerCase().includes('timeout') || error?.message?.toLowerCase().includes('network');
    
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-red-500 space-y-4">
        <AlertCircle className="w-12 h-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">
          {isTimeout 
            ? "AI analysis is taking longer than expected." 
            : "The governance service is temporarily unavailable."}
        </p>
        <p className="text-sm text-gray-500 max-w-md text-center">
          {isTimeout 
            ? "The backend AI model might be cold-starting or overwhelmed. Please try again."
            : "An unexpected error occurred while generating your brief. Please verify your connection or try again."}
        </p>
        <Button onClick={() => refetch()} variant="outline" className="mt-4">
          <RefreshCw className="w-4 h-4 mr-2" /> Retry Analysis
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Daily Governance Brief</h1>
        <div className="text-sm text-gray-500">{new Date().toLocaleDateString()}</div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="bg-white rounded-lg border border-red-200 shadow-sm overflow-hidden">
          <div className="bg-red-50 px-4 py-3 border-b border-red-200 flex items-center gap-2 text-red-800 font-semibold">
            <AlertTriangle size={18} /> Critical Issues
          </div>
          <div className="p-4 space-y-3">
            {data.critical_issues.length === 0 ? (
              <p className="text-gray-500 text-sm">No critical issues reported.</p>
            ) : (
              data.critical_issues.map((issue, idx) => (
                <div key={idx} className="flex gap-2 text-sm text-gray-700">
                  <div className="mt-0.5 text-red-500">•</div>
                  <div>{issue.description || issue.title || JSON.stringify(issue)}</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-orange-200 shadow-sm overflow-hidden">
          <div className="bg-orange-50 px-4 py-3 border-b border-orange-200 flex items-center gap-2 text-orange-800 font-semibold">
            <Info size={18} /> Attention Needed
          </div>
          <div className="p-4 space-y-3">
            {data.attention_items.length === 0 ? (
              <p className="text-gray-500 text-sm">No items need attention.</p>
            ) : (
              data.attention_items.map((item, idx) => (
                <div key={idx} className="flex gap-2 text-sm text-gray-700">
                  <div className="mt-0.5 text-orange-500">•</div>
                  <div>{item.description || item.title || JSON.stringify(item)}</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-green-200 shadow-sm overflow-hidden">
          <div className="bg-green-50 px-4 py-3 border-b border-green-200 flex items-center gap-2 text-green-800 font-semibold">
            <CheckCircle size={18} /> Positive Developments
          </div>
          <div className="p-4 space-y-3">
            {data.positive_developments.length === 0 ? (
              <p className="text-gray-500 text-sm">No new developments.</p>
            ) : (
              data.positive_developments.map((pos, idx) => (
                <div key={idx} className="flex gap-2 text-sm text-gray-700">
                  <div className="mt-0.5 text-green-500">•</div>
                  <div>{pos.description || pos.title || JSON.stringify(pos)}</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-blue-200 shadow-sm overflow-hidden">
          <div className="bg-blue-50 px-4 py-3 border-b border-blue-200 flex items-center gap-2 text-blue-800 font-semibold">
            <Lightbulb size={18} /> AI Recommendations
          </div>
          <div className="p-4 space-y-3">
            {data.recommendations.length === 0 ? (
              <p className="text-gray-500 text-sm">No recommendations at this time.</p>
            ) : (
              data.recommendations.map((rec, idx) => (
                <div key={idx} className="flex gap-2 text-sm text-gray-700">
                  <div className="mt-0.5 text-blue-500">•</div>
                  <div>{rec.description || rec.title || JSON.stringify(rec)}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
