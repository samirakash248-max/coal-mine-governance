import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ShieldAlert } from 'lucide-react';

export default function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-graphite-950 p-4">
      <div className="text-center space-y-6 max-w-md bg-graphite-900 p-8 rounded-xl border border-graphite-800 shadow-xl">
        <div className="flex justify-center">
          <ShieldAlert className="h-24 w-24 text-red-500" />
        </div>
        <h1 className="text-3xl font-bold text-white">Access Denied</h1>
        <p className="text-graphite-400">
          You do not have the required permissions to view this sector. Please contact your site supervisor if you believe this is an error.
        </p>
        <Button 
          onClick={() => navigate('/')}
          className="bg-graphite-800 hover:bg-graphite-700 text-white border border-graphite-700 w-full"
        >
          Return to Dashboard
        </Button>
      </div>
    </div>
  );
}
