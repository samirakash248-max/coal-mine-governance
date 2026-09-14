import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocument, useVerifyDocument, VerifyDocumentPayload } from '@/hooks/useDocuments';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function VerifyDocument() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: document, isLoading } = useDocument(id!);
  const verifyMutation = useVerifyDocument(id!);

  const [formData, setFormData] = useState<VerifyDocumentPayload>({
    title: '',
    document_number: '',
    category: '',
    issue_date: '',
    expiry_date: '',
  });

  useEffect(() => {
    if (document) {
      setFormData({
        title: document.title || '',
        document_number: document.document_number || '',
        category: document.category || '',
        issue_date: document.issue_date || '',
        expiry_date: document.expiry_date || '',
      });
    }
  }, [document]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await verifyMutation.mutateAsync(formData);
    navigate('/documents');
  };

  if (isLoading) {
    return <div className="p-6">Loading document details...</div>;
  }

  if (!document) {
    return <div className="p-6">Document not found.</div>;
  }

  return (
    <div className="p-6 h-[calc(100vh-64px)]">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Verify Document</h1>
        <Button variant="outline" onClick={() => navigate('/documents')}>
          Back to Library
        </Button>
      </div>

      <div className="flex gap-6 h-[calc(100%-80px)]">
        {/* Left Side: Preview */}
        <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-md border flex items-center justify-center">
          <p className="text-gray-500 dark:text-gray-400">Document Preview</p>
        </div>

        {/* Right Side: Form */}
        <div className="w-[400px] shrink-0">
          <Card>
            <CardHeader>
              <CardTitle>Extracted Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Title</label>
                  <Input name="title" value={formData.title} onChange={handleChange} required />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Document Number</label>
                  <Input name="document_number" value={formData.document_number} onChange={handleChange} required />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Category</label>
                  <Input name="category" value={formData.category} onChange={handleChange} required />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Issue Date</label>
                  <Input name="issue_date" type="date" value={formData.issue_date} onChange={handleChange} required />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">Expiry Date</label>
                  <Input name="expiry_date" type="date" value={formData.expiry_date} onChange={handleChange} required />
                </div>
                
                <Button type="submit" disabled={verifyMutation.isPending} className="mt-4">
                  {verifyMutation.isPending ? 'Verifying...' : 'Verify Document'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
