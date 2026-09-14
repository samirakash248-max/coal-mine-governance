import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useAuth } from '../providers/AuthProvider';
import { apiClient } from '../api/client';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Login() {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);
    try {
      if (mode === 'signin') {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await apiClient.post('/api/v1/auth/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        
        if (response.data?.access_token) {
          login(response.data.access_token);
          navigate(from, { replace: true });
        } else {
          throw new Error('Invalid response from server: Missing access token');
        }
      } else {
        // Mock signup flow as backend endpoint is not implemented
        setTimeout(() => {
          setSuccess('Account created successfully! Please sign in.');
          setMode('signin');
          setIsLoading(false);
        }, 1000);
        return;
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      if (mode === 'signin') setIsLoading(false);
    }
  };

  const handleGoogleAuth = async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await apiClient.get('/api/v1/auth/google/login');
      if (response.data?.url && response.data?.state) {
        sessionStorage.setItem('oauth_state', response.data.state);
        window.location.href = response.data.url;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate Google Login.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-graphite-950 p-4">
      <Card className="w-full max-w-md bg-graphite-900 border-graphite-800 text-graphite-100 shadow-xl">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-mining-amber-500 text-graphite-950">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight text-white">
            CoalMine Auth
          </CardTitle>
          <CardDescription className="text-graphite-400">
            {mode === 'signin' ? 'Enter your credentials to access the system' : 'Create a new account'}
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-md">
                {error}
              </div>
            )}
            {success && (
              <div className="p-3 text-sm text-green-500 bg-green-500/10 border border-green-500/20 rounded-md">
                {success}
              </div>
            )}
            
            {mode === 'signup' && (
              <div className="space-y-2">
                <label htmlFor="fullName" className="text-sm font-medium leading-none text-graphite-300">
                  Full Name
                </label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="John Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="bg-graphite-800 border-graphite-700 text-graphite-100 placeholder:text-graphite-500 focus-visible:ring-mining-amber-500"
                  required={mode === 'signup'}
                />
              </div>
            )}
            
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium leading-none text-graphite-300">
                Email / Username
              </label>
              <Input
                id="email"
                type="text"
                placeholder="manager.raniganj@coalmine.gov.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-graphite-800 border-graphite-700 text-graphite-100 placeholder:text-graphite-500 focus-visible:ring-mining-amber-500"
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium leading-none text-graphite-300">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-graphite-800 border-graphite-700 text-graphite-100 focus-visible:ring-mining-amber-500"
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-mining-amber-500 hover:bg-mining-amber-600 text-graphite-950 font-semibold"
            >
              {isLoading ? (mode === 'signin' ? 'Signing In...' : 'Signing Up...') : (mode === 'signin' ? 'Sign In' : 'Sign Up')}
            </Button>
            
            <div className="relative w-full">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-graphite-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-graphite-900 px-2 text-graphite-400">Or continue with</span>
              </div>
            </div>
            
            <Button
              type="button"
              variant="outline"
              className="w-full bg-graphite-800 border-graphite-700 text-graphite-100 hover:bg-graphite-700 hover:text-white"
              onClick={handleGoogleAuth}
            >
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
              Google
            </Button>

            <div className="text-center text-sm text-graphite-400 mt-4">
              {mode === 'signin' ? (
                <>
                  Don't have an account?{' '}
                  <button type="button" onClick={() => setMode('signup')} className="text-mining-amber-500 hover:underline">
                    Sign up
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{' '}
                  <button type="button" onClick={() => setMode('signin')} className="text-mining-amber-500 hover:underline">
                    Sign in
                  </button>
                </>
              )}
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

