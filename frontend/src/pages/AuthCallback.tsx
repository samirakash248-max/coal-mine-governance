import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../providers/AuthProvider';
import { apiClient } from '../api/client';
import { Loader2 } from 'lucide-react';

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const oauthError = searchParams.get('error');
    if (oauthError) {
      setError('Google Authentication was denied or failed.');
      return;
    }

    const state = searchParams.get('state');
    const storedState = sessionStorage.getItem('oauth_state');
    
    if (!state || !storedState || state !== storedState) {
      setError('Security validation failed. State mismatch or missing.');
      return;
    }
    
    sessionStorage.removeItem('oauth_state');

    const code = searchParams.get('code');
    if (!code) {
      setError('No authorization code found.');
      return;
    }

    const exchangeCode = async () => {
      try {
        const response = await apiClient.post('/api/v1/auth/google/callback', { code });
        if (response.data?.access_token) {
          login(response.data.access_token);
          navigate('/', { replace: true });
        } else {
          setError('Invalid response from server.');
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
      }
    };

    exchangeCode();
  }, [searchParams, login, navigate]);

  if (error) {
    return (
      <div className="min-h-screen bg-graphite-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md bg-graphite-900 py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-graphite-800">
          <div className="text-center text-red-500 mb-4">{error}</div>
          <button 
            onClick={() => navigate('/login')}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-mining-amber-600 hover:bg-mining-amber-700"
          >
            Return to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-graphite-950 flex flex-col justify-center items-center py-12">
      <Loader2 className="h-12 w-12 text-mining-amber-500 animate-spin mb-4" />
      <h2 className="text-xl text-graphite-100 font-semibold">Completing Google Sign In...</h2>
    </div>
  );
}
