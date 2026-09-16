import { useState } from 'react';
ï»¿import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Skeleton } from '../../components/ui/skeleton';
import { Button } from '../../components/ui/button';
import { AlertTriangle, Info, AlertCircle, ShieldAlert } from 'lucide-react';
import { useHighRiskCases, RiskEvent } from '../../hooks/useRisk';
import { useDashboardSummary } from '../../hooks/useDashboard';
import { useEntityAuditLogs } from '../../hooks/useAudit';

export default function RiskIntelligence() {
  const { data: cases, isLoading: isLoadingCases, isError: isErrorCases, refetch: refetchCases } = useHighRiskCases();
  const { data: summary, isLoading: isLoadingSummary } = useDashboardSummary();
  const [selectedCase, setSelectedCase] = useState<RiskEvent | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Risk Intelligence Center</h1>
          <p className="text-gray-500">Real-time risk scoring, explainability, and safety cases.</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-red-50 border-red-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="text-red-600 h-5 w-5" />
              <h3 className="text-red-800 font-semibold text-sm">Critical Risk Cases</h3>
            </div>
            {isLoadingSummary ? <Skeleton className="h-8 w-16 bg-red-200" /> : <div className="text-3xl font-bold text-red-700">{summary?.critical_findings_count || 0}</div>}
          </CardContent>
        </Card>
        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="text-orange-600 h-5 w-5" />
              <h3 className="text-orange-800 font-semibold text-sm">High Risk Cases</h3>
            </div>
            {isLoadingSummary ? <Skeleton className="h-8 w-16 bg-orange-200" /> : <div className="text-3xl font-bold text-orange-700">{(summary?.high_critical_risk_cases || 0) - (summary?.critical_findings_count || 0)}</div>}
          </CardContent>
        </Card>
        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <ShieldAlert className="text-yellow-600 h-5 w-5" />
              <h3 className="text-yellow-800 font-semibold text-sm">Overdue Actions</h3>
            </div>
            {isLoadingSummary ? <Skeleton className="h-8 w-16 bg-yellow-200" /> : <div className="text-3xl font-bold text-yellow-700">{summary?.overdue_actions_count || 0}</div>}
          </CardContent>
        </Card>
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <Info className="text-blue-600 h-5 w-5" />
              <h3 className="text-blue-800 font-semibold text-sm">AI Overrides</h3>
            </div>
            {isLoadingSummary ? <Skeleton className="h-8 w-16 bg-blue-200" /> : <div className="text-3xl font-bold text-blue-700">{summary?.ai_overrides_count || 0}</div>}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>High-Risk Cases</CardTitle>
              <CardDescription>Select a case for risk explainability</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingCases ? (
                <div className="space-y-3">
                  {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-16 w-full" />)}
                </div>
              ) : isErrorCases ? (
                <div className="p-4 text-red-500 bg-red-50 rounded-lg text-sm flex flex-col items-start gap-2">
                  <p>Failed to load risk cases.</p>
                  <Button variant="outline" size="sm" onClick={() => refetchCases()}>Retry</Button>
                </div>
              ) : !cases || cases.length === 0 ? (
                <div className="text-gray-500 text-sm py-4">No high or critical risk cases found.</div>
              ) : (
                <div className="space-y-2 h-[500px] overflow-y-auto pr-2">
                  {cases.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => setSelectedCase(c)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedCase?.id === c.id 
                          ? 'bg-blue-50 border-blue-200' 
                          : 'bg-white border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-medium text-sm text-gray-900 truncate pr-2">{c.title || c.type}</span>
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          c.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                        }`}>
                          {c.risk_level}
                        </span>
                      </div>
                      <div className="flex justify-between items-end">
                        <span className="text-xs text-gray-500 truncate">{new Date(c.created_at).toLocaleDateString()}</span>
                        {c.risk_score !== null && (
                          <span className="text-xs font-semibold text-gray-700">Score: {c.risk_score}/100</span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          {selectedCase ? (
            <CaseDetailView riskCase={selectedCase} />
          ) : (
            <Card className="h-full flex items-center justify-center bg-gray-50 border-dashed">
              <div className="text-center text-gray-500">
                <Info className="h-12 w-12 mx-auto text-gray-300 mb-2" />
                <p>Select a case from the list to view its risk factors and audit trail.</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

import { aiApiClient } from '@/api/client';
import { toast } from 'sonner';

function CaseDetailView({ riskCase }: { riskCase: RiskEvent }) {
  const { data: auditLogs, isLoading: isLoadingAudit } = useEntityAuditLogs('SafetyEvent', riskCase.id);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const response = await aiApiClient.post('/api/v1/copilot/chat', {
        message: `Analyze this risk case: Title: ${riskCase.title}, Description: ${riskCase.description}, Score: ${riskCase.risk_score}, Level: ${riskCase.risk_level}. What are the likely causes and recommended actions?`,
        mine_id: riskCase.mine_id
      });
      setAiAnalysis(response.data.answer);
    } catch (err) {
      toast.error("AI Analysis failed or is unavailable.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b border-gray-100 pb-4">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-gray-500 uppercase">{riskCase.type}</span>
              {riskCase.is_ai_overridden && (
                <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-medium">AI OVERRIDDEN</span>
              )}
            </div>
            <CardTitle>{riskCase.title || 'Untitled Case'}</CardTitle>
            <CardDescription className="mt-2">{riskCase.description || 'No description provided.'}</CardDescription>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${riskCase.risk_level === 'CRITICAL' ? 'text-red-600' : 'text-orange-600'}`}>
              {riskCase.risk_score !== null ? riskCase.risk_score : '--'}
            </div>
            <div className="text-xs font-medium text-gray-500 uppercase mt-1">Risk Score</div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto pt-6 space-y-8">
        
        {/* AI Analysis Section */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-purple-500" />
              AI Assistant Analysis
            </h3>
            <Button size="sm" variant="outline" onClick={handleAnalyze} disabled={isAnalyzing}>
              {isAnalyzing ? "Analyzing..." : "Request AI Analysis"}
            </Button>
          </div>
          
          {aiAnalysis && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="text-xs font-bold text-purple-800 mb-2 uppercase tracking-wider">
                AI-Generated Analysis — Verify before taking regulatory action
              </div>
              <div className="text-sm text-purple-900 whitespace-pre-wrap leading-relaxed">
                {aiAnalysis}
              </div>
            </div>
          )}
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-gray-500" />
            Explainable Risk Factors
          </h3>
          {riskCase.risk_factors && Object.keys(riskCase.risk_factors).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(riskCase.risk_factors).map(([factor, details]: [string, any], idx) => (
                <div key={idx} className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-medium text-sm text-gray-800 capitalize">{factor.replace(/_/g, ' ')}</span>
                    <span className="text-xs font-semibold text-gray-600">{details.impact || details.contribution || ''}</span>
                  </div>
                  <p className="text-xs text-gray-600">{details.reason || details.description || JSON.stringify(details)}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">No specific risk factors were recorded for this case by the backend engine.</p>
          )}
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-gray-500" />
            Audit Trail & Timeline
          </h3>
          {isLoadingAudit ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : !auditLogs || auditLogs.length === 0 ? (
            <p className="text-sm text-gray-500 italic">No historical audit events found for this case.</p>
          ) : (
            <div className="relative border-l border-gray-200 ml-2 space-y-6">
              {auditLogs.map((log: any) => (
                <div key={log.id} className="pl-6 relative">
                  <div className="absolute w-3 h-3 bg-gray-200 rounded-full -left-[6.5px] top-1.5 border-2 border-white" />
                  <div className="flex items-start justify-between mb-1">
                    <div>
                      <span className="text-sm font-semibold text-gray-900">{log.action}</span>
                      <span className="text-xs text-gray-500 ml-2">by {log.role || 'SYSTEM'}</span>
                    </div>
                    <span className="text-[10px] text-gray-400 font-mono">{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                  {log.after_state && (
                    <div className="mt-2 bg-gray-50 rounded border border-gray-100 p-2 text-xs font-mono text-gray-600 overflow-x-auto">
                      {JSON.stringify(log.after_state, null, 2)}
                    </div>
                  )}
                  <div className="text-[9px] text-gray-400 font-mono mt-1" title="Cryptographic Hash Signature">
                    Hash: {log.hash_signature?.substring(0, 16)}...
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

