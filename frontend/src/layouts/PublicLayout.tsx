import { Outlet, Link } from 'react-router-dom';
import { Mountain } from 'lucide-react';

export function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 text-graphite-900 font-sans">
      <header className="flex h-16 shrink-0 items-center gap-4 border-b border-graphite-200 bg-white px-4 shadow-sm sm:px-6 lg:px-8">
        <Link to="/public" className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-mining-amber-500 text-graphite-950">
            <Mountain size={20} className="stroke-[2.5px]" />
          </div>
          <span className="text-xl font-bold tracking-tight text-graphite-900">CoalMine Public Portal</span>
        </Link>
        <div className="ml-auto">
          <Link to="/login" className="text-sm font-medium text-graphite-600 hover:text-graphite-900">
            Staff Login
          </Link>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-5xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
