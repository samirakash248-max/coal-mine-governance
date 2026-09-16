import { VoiceRecorder } from '../../components/ui/VoiceRecorder';
import { useState } from 'react';
import { useCreateFieldEvent, useAIClassify } from '../../hooks/useFieldOps';

export default function ReportEvent() {
  const [type, setType] = useState<'INCIDENT' | 'NEAR_MISS' | 'HAZARD_OBSERVATION' | 'UNSAFE_CONDITION'>('HAZARD_OBSERVATION');
  const [severity, setSeverity] = useState<'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'>('LOW');
  const [description, setDescription] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [success, setSuccess] = useState(false);

  const { mutate: createEvent, isPending } = useCreateFieldEvent();
  const { mutate: classifyEvent, isPending: isClassifying, data: aiSuggestion, error: aiError } = useAIClassify();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createEvent(
      { type, severity, description, is_anonymous: isAnonymous },
      {
        onSuccess: () => {
          setSuccess(true);
          setDescription('');
        }
      }
    );
  };

  const handleAIClassify = () => {
    if (!description.trim()) return;
    classifyEvent(description);
  };

  const applyAISuggestion = () => {
    if (aiSuggestion?.event_type) {
        const typeMap: Record<string, any> = {
            'hazard_observation': 'HAZARD_OBSERVATION',
            'unsafe_condition': 'UNSAFE_CONDITION',
            'near_miss': 'NEAR_MISS',
            'incident': 'INCIDENT'
        };
        const mapped = typeMap[aiSuggestion.event_type.toLowerCase()];
        if (mapped) setType(mapped);
    }
    if (aiSuggestion?.severity && aiSuggestion.severity !== 'unknown') {
        setSeverity(aiSuggestion.severity.toUpperCase() as any);
    }
  };

  if (success) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-green-200">
        <h2 className="text-2xl font-bold text-green-700 mb-4">Observation Submitted</h2>
        <p className="text-gray-700 mb-6">Thank you for helping improve safety in our operations.</p>
        <button 
          onClick={() => setSuccess(false)}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg font-medium"
        >
          Submit Another Observation
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Submit Safety Observation</h1>
      <p className="text-gray-600 mb-6">Help improve safety by reporting hazards, near misses, or unsafe conditions.</p>
      
      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        
        <div className="space-y-2">
          <div className="flex justify-between items-center"><label className="block text-sm font-medium text-gray-700">Description</label><VoiceRecorder onTranscriptionComplete={(t: string) => setDescription(prev => prev + " " + t)} /></div>
          <textarea 
            value={description} 
            onChange={e => setDescription(e.target.value)}
            required
            rows={5}
            placeholder="Describe what you observed..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-mining-amber-500 resize-none"
          />
          <div className="flex justify-end">
            <button
                type="button"
                onClick={handleAIClassify}
                disabled={isClassifying || !description.trim()}
                className="text-sm px-3 py-1.5 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-md font-medium flex items-center gap-1 disabled:opacity-50"
            >
                {isClassifying ? 'Analyzing...' : '✨ Ask AI Copilot to Classify'}
            </button>
          </div>
          
          {aiError && (
              <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">
                  Failed to connect to experimental AI assistant.
              </div>
          )}
          
          {aiSuggestion && !aiError && (
              <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-blue-900 flex items-center gap-2">
                          ✨ Experimental AI Suggestion
                      </h4>
                      <button 
                        type="button"
                        onClick={applyAISuggestion}
                        className="text-xs px-2 py-1 bg-white border border-blue-200 text-blue-700 rounded hover:bg-blue-50"
                      >
                          Apply Values
                      </button>
                  </div>
                  <p className="text-xs text-blue-600 mb-3">Note: Current local model (Qwen 0.6B) is experimental and has low semantic accuracy (~14%). Please verify all suggestions.</p>
                  <ul className="text-sm text-blue-800 space-y-1">
                      <li><strong>Event Type:</strong> {aiSuggestion.event_type || 'Unknown'}</li>
                      <li><strong>Category:</strong> {aiSuggestion.category || 'Unknown'}</li>
                      <li><strong>Severity:</strong> {aiSuggestion.severity || 'Unknown'}</li>
                      <li><strong>Needs Review:</strong> {aiSuggestion.needs_human_review ? 'Yes' : 'No'}</li>
                  </ul>
              </div>
          )}
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Observation Type</label>
          <select 
            value={type} 
            onChange={e => setType(e.target.value as any)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-mining-amber-500 bg-white"
          >
            <option value="HAZARD_OBSERVATION">Hazard Observation</option>
            <option value="UNSAFE_CONDITION">Unsafe Condition</option>
            <option value="NEAR_MISS">Near Miss</option>
            <option value="INCIDENT">Incident</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Severity Potential</label>
          <select 
            value={severity} 
            onChange={e => setSeverity(e.target.value as any)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-mining-amber-500 bg-white"
          >
            <option value="LOW">Low - Unlikely to cause injury</option>
            <option value="MEDIUM">Medium - Minor injury possible</option>
            <option value="HIGH">High - Serious injury possible</option>
            <option value="CRITICAL">Critical - Life threatening</option>
          </select>
        </div>

        <div className="flex items-center gap-3 py-2">
          <input 
            type="checkbox" 
            id="anonymous" 
            checked={isAnonymous}
            onChange={e => setIsAnonymous(e.target.checked)}
            className="w-5 h-5 text-mining-amber-600 rounded focus:ring-mining-amber-500"
          />
          <label htmlFor="anonymous" className="text-sm font-medium text-gray-700 select-none">
            Submit anonymously
          </label>
        </div>

        <button 
          type="submit" 
          disabled={isPending || !description.trim()}
          className="w-full py-4 bg-mining-amber-500 hover:bg-mining-amber-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white text-lg font-semibold rounded-lg transition-colors"
        >
          {isPending ? 'Submitting...' : 'Submit Observation'}
        </button>
      </form>
    </div>
  );
}
