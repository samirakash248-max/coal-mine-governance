import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

export default function DocumentLibrary() {
  const navigate = useNavigate();
  const { data: documents, isLoading } = useDocuments();
  const uploadMutation = useUploadDocument();
  const [file, setFile] = useState<File | null>(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0] || null);
    }
  };

  const handleUpload = async () => {
    if (file) {
      await uploadMutation.mutateAsync(file);
      setIsUploadOpen(false);
      setFile(null);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Document Library</h1>
        <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
          <DialogTrigger asChild>
            <Button>Upload Document</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload New Document</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col gap-4 py-4">
              <Input type="file" onChange={handleFileChange} />
              <Button onClick={handleUpload} disabled={!file || uploadMutation.isPending}>
                {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Document Number</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Issue Date</TableHead>
              <TableHead>Expiry Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-4">Loading...</TableCell>
              </TableRow>
            ) : documents?.length ? (
              documents.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>{doc.title}</TableCell>
                  <TableCell>{doc.document_number}</TableCell>
                  <TableCell>{doc.category}</TableCell>
                  <TableCell>{doc.issue_date}</TableCell>
                  <TableCell>{doc.expiry_date}</TableCell>
                  <TableCell>{doc.status}</TableCell>
                  <TableCell className="text-right">
                    {doc.status === 'PENDING_VERIFICATION' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/documents/${doc.id}/verify`)}
                      >
                        Verify
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-4">No documents found.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
