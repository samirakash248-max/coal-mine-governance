import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-900 p-4">
          <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg border border-red-100 text-center">
            <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
            <p className="text-gray-500 mb-6">
              The application encountered an unexpected rendering error. 
              Your session is safe, but this component could not be displayed.
            </p>
            <Button 
              onClick={() => window.location.reload()} 
              className="w-full flex items-center justify-center"
            >
              <RefreshCw className="w-4 h-4 mr-2" /> Reload Application
            </Button>
            {process.env.NODE_ENV !== 'production' && this.state.error && (
              <div className="mt-6 text-left p-4 bg-gray-100 rounded text-xs text-red-800 overflow-x-auto">
                <p className="font-semibold">{this.state.error.name}: {this.state.error.message}</p>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

