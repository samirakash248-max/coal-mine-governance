import { AlertTriangle, Info, CheckCircle, Lightbulb } from 'lucide-react';
import { useDailyBrief } from '../hooks/useCopilot';

export default function DailyBrief() {
  const { data, isLoading, isError } = useDailyBrief();

  if (isLoading) return <div className="p-6 text-gray-500">Loading daily brief...</div>;
  if (isError || !data) return <div className="p-6 text-red-500">Failed to load daily brief.</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-graphite-900">Daily Governance Brief</h1>
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

        <div className="bg-white rounded-lg border border-primary-200 shadow-sm overflow-hidden">
          <div className="bg-primary-50 px-4 py-3 border-b border-primary-200 flex items-center gap-2 text-primary-800 font-semibold">
            <Lightbulb size={18} /> AI Recommendations
          </div>
          <div className="p-4 space-y-3">
            {data.recommendations.length === 0 ? (
              <p className="text-gray-500 text-sm">No recommendations at this time.</p>
            ) : (
              data.recommendations.map((rec, idx) => (
                <div key={idx} className="flex gap-2 text-sm text-gray-700">
                  <div className="mt-0.5 text-primary-500">•</div>
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
