import { useState } from 'react';
import { useGrievances } from '../../hooks/useGrievances';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Sparkles, Plus, MessageSquare, AlertCircle } from 'lucide-react';

export default function GrievancesList() {
  const { grievances, isLoading, isError, createGrievance, applyAiSuggestions } = useGrievances();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) return;
    setIsSubmitting(true);
    try {
      await createGrievance.mutateAsync({ title, description });
      setTitle('');
      setDescription('');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) return <div className="p-6 text-gray-500">Loading grievances...</div>;

  if (isError) {
    return (
      <div className="p-6">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6 flex items-center text-red-700">
            <AlertCircle className="w-5 h-5 mr-3" />
            <p>Failed to load grievances. Please try again or contact support if the issue persists.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Grievances</h1>
          <p className="text-gray-500">Manage worker grievances and AI suggestions</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {grievances?.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center flex flex-col items-center">
                <MessageSquare className="w-12 h-12 text-gray-400 mb-3" />
                <h3 className="text-lg font-medium text-gray-900">No Grievances Found</h3>
                <p className="text-gray-500 mt-1">There are currently no reported grievances.</p>
              </CardContent>
            </Card>
          ) : (
            grievances?.map((grievance: any) => (
              <Card key={grievance.id} className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{grievance.title}</CardTitle>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      grievance.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                      grievance.status === 'RESOLVED' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {grievance.status}
                    </span>
                  </div>
                  <CardDescription>Reported on {new Date(grievance.created_at).toLocaleDateString()}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 whitespace-pre-wrap">{grievance.description}</p>
                  
                  <div className="mt-4 flex gap-2">
                    {grievance.category && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-primary-50 text-primary-700">
                        Category: {grievance.category}
                      </span>
                    )}
                    {grievance.priority && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-red-50 text-red-700">
                        Priority: {grievance.priority}
                      </span>
                    )}
                  </div>

                  {grievance.status === 'PENDING' && grievance.ai_suggestions && (
                    <div className="mt-4 p-4 bg-amber-50/50 rounded-lg border border-amber-100">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center text-amber-700 font-medium text-sm">
                            <Sparkles className="w-4 h-4 mr-1.5" />
                            AI Suggestion
                          </div>
                          <p className="text-sm text-amber-900/80">
                            <strong>Category:</strong> {grievance.ai_suggestions.suggested_category} <br/>
                            <strong>Priority:</strong> {grievance.ai_suggestions.suggested_priority}
                          </p>
                          <p className="text-xs text-amber-700/70 mt-1 italic">
                            Reasoning: {grievance.ai_suggestions.reasoning}
                          </p>
                        </div>
                        <Button 
                          size="sm" 
                          variant="secondary"
                          onClick={() => applyAiSuggestions.mutate({ 
                            id: grievance.id, 
                            category: grievance.ai_suggestions.suggested_category 
                          })}
                          disabled={applyAiSuggestions.isPending}
                          className="bg-amber-100 hover:bg-amber-200 text-amber-700 border-0"
                        >
                          Approve AI Suggestion
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-lg">
                <Plus className="w-5 h-5 mr-2 text-gray-500" />
                Submit Grievance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <Input 
                    placeholder="Brief description of the issue" 
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    className="flex min-h-[120px] w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Provide detailed information..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? 'Submitting...' : 'Submit Grievance'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
