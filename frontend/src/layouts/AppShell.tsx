import { useState } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { 
  Home, Map, Calendar, Search, Shield, 
  AlertTriangle, BarChart3, Settings, Menu, Cloud, X, ChevronRight, LogOut, Mountain, CheckCircle, Map as MapIcon, FileText, Newspaper, Sparkles, MessageSquare
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useUser } from '../hooks/useUser';
import { useAuth } from '../providers/AuthProvider';
import { NotificationCenter } from '../components/NotificationCenter';
import { useOfflineSync } from '../hooks/useOfflineSync';
import { Badge } from '../components/ui/badge';
import { CopilotDrawer } from '../components/Copilot/CopilotDrawer';

const navItems = [
  { name: 'Dashboard', to: '/dashboard', icon: Home, perm: 'dashboard:read' },
  { name: 'Daily Brief', to: '/daily-brief', icon: Newspaper, perm: 'dashboard:read' },
  { name: 'Governance Map', to: '/gis', icon: MapIcon, perm: 'mine:read' },
  { name: 'Weather Risk', to: '/weather', icon: Cloud, perm: 'weather:read' },
  { name: 'Mines', to: '/mines', icon: Map, perm: 'mine:read' },
  { name: 'Compliance Calendar', to: '/compliance/calendar', icon: Calendar, perm: 'compliance:read' },
  { name: 'Report Observation', to: '/field/report', icon: AlertTriangle, perm: 'safety:create' },
  { name: 'Corrective Actions', to: '/field/actions', icon: CheckCircle, perm: 'safety:read' },
  { name: 'Document Library', to: '/documents', icon: FileText, perm: 'document:read' },
  { name: 'Inspections', to: '/inspections', icon: Search, perm: 'inspection:read' },
  { name: 'Safety', to: '/safety', icon: Shield, perm: 'safety:read' },
  { name: 'Risk Intelligence', to: '/risk', icon: AlertTriangle, perm: 'risk:read' },
  { name: 'Audit Trail', to: '/audit', icon: Shield, perm: 'audit:read' },
  { name: 'Analytics', to: '/analytics', icon: BarChart3, perm: 'report:read' },
  { name: 'Reports', to: '/reports', icon: FileText, perm: 'report:read' },
  { name: 'Grievances', to: '/grievances', icon: MessageSquare, perm: 'grievance:read' },
];

export function AppShell() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isCopilotOpen, setCopilotOpen] = useState(false);
  const { data: userProfile } = useUser();
  const { logout, hasPermission } = useAuth();
  const { isOffline, isSyncing } = useOfflineSync();

  return (
    <div className="flex h-screen w-full bg-gray-50 overflow-hidden text-graphite-900 font-sans">
      {/* Mobile sidebar overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 z-40 bg-graphite-950/50 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={twMerge(
        clsx(
          "fixed inset-y-0 left-0 z-50 w-64 bg-graphite-950 text-white transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 flex flex-col shadow-xl",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )
      )}>
        {/* Logo area */}
        <div className="flex h-16 shrink-0 items-center gap-3 px-6 border-b border-graphite-800">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-mining-amber-500 text-graphite-950">
            <Mountain size={20} className="stroke-[2.5px]" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">CoalMine</span>
          <button 
            className="ml-auto text-graphite-400 hover:text-white lg:hidden"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
          {navItems.filter(item => hasPermission(item.perm)).map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              className={({ isActive }) => clsx(
                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors relative",
                isActive 
                  ? "bg-graphite-800 text-white" 
                  : "text-graphite-300 hover:bg-graphite-800/50 hover:text-white"
              )}
            >
              {({ isActive }) => (
                <>
                  <item.icon 
                    size={18} 
                    className={clsx(
                      "shrink-0 transition-colors",
                      isActive ? "text-mining-amber-500" : "text-graphite-500 group-hover:text-graphite-300"
                    )} 
                  />
                  {item.name}
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -mt-4 h-8 w-1 rounded-r bg-mining-amber-500" aria-hidden="true" />
                  )}
                </>
              )}
            </NavLink>
          ))}

          <div className="mt-8 pt-4 border-t border-graphite-800">
            <NavLink
              to="/settings"
              className={({ isActive }) => clsx(
                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors relative",
                isActive ? "bg-graphite-800 text-white" : "text-graphite-300 hover:bg-graphite-800/50 hover:text-white"
              )}
            >
              {({ isActive }) => (
                <>
                  <Settings 
                    size={18} 
                    className={clsx(
                      "shrink-0 transition-colors",
                      isActive ? "text-mining-amber-500" : "text-graphite-500 group-hover:text-graphite-300"
                    )} 
                  />
                  Settings
                </>
              )}
            </NavLink>
          </div>
        </nav>

        {/* Sidebar footer */}
        <div className="p-4 border-t border-graphite-800 text-xs text-graphite-500 font-mono">
          v0.1.0-alpha
        </div>
      </aside>

      {/* Main content wrapper */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="flex h-16 shrink-0 items-center gap-4 border-b border-graphite-200 bg-white px-4 shadow-subtle sm:px-6 lg:px-8">
          <button 
            className="text-graphite-500 hover:text-graphite-700 lg:hidden"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu size={24} />
          </button>
          
          <div className="flex flex-1 items-center justify-between">
            {/* Breadcrumb placeholder */}
            <nav className="flex text-sm font-medium text-graphite-500 hidden sm:block">
              <ol className="flex items-center space-x-2">
                <li><span className="hover:text-graphite-900 cursor-pointer">Home</span></li>
                <li><ChevronRight size={16} className="text-graphite-300" /></li>
                <li><span className="text-graphite-900">Dashboard</span></li>
              </ol>
            </nav>

            <div className="flex items-center gap-4 ml-auto">
              {isOffline ? (
                <Badge variant="outline" className="text-red-500 border-red-500">Offline</Badge>
              ) : isSyncing ? (
                <Badge variant="outline" className="text-primary-500 border-primary-500">Syncing...</Badge>
              ) : null}
              <NotificationCenter />
              <button 
                onClick={() => setCopilotOpen(true)}
                className="p-1.5 text-graphite-400 hover:text-mining-amber-500 transition-colors rounded-full hover:bg-mining-amber-50"
                title="AI Copilot"
              >
                <Sparkles size={20} />
              </button>
              <div className="h-8 border-l border-graphite-200 mx-1"></div>
              
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 rounded-full p-1 pr-2 hover:bg-graphite-50 transition-colors border border-transparent hover:border-graphite-200">
                  <div className="h-8 w-8 rounded-full bg-earth-200 flex items-center justify-center text-earth-800 font-bold text-sm">
                    {userProfile?.full_name ? userProfile.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <span className="text-sm font-medium text-graphite-700 hidden sm:block">
                    {userProfile?.full_name || 'Loading...'}
                  </span>
                </div>
                <button 
                  onClick={logout}
                  className="p-1.5 text-graphite-400 hover:text-red-600 transition-colors rounded-full hover:bg-red-50"
                  title="Logout"
                >
                  <LogOut size={20} />
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main scrollable area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
      
      <CopilotDrawer open={isCopilotOpen} onClose={() => setCopilotOpen(false)} />
    </div>
  );
}





